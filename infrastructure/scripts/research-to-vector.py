#!/usr/bin/env python3
"""
research-to-vector.py - Query Gemini and store directly in Qdrant

Usage:
    python research-to-vector.py "topic" "Your detailed question" "domain" "tag1,tag2,tag3"

Example:
    python research-to-vector.py "candlestick-patterns" "Explain all candlestick patterns..." "technical-analysis" "candlesticks,patterns,trading"

Features:
- Retries on empty Gemini response (rate limiting protection)
- Generates embeddings via Ollama nomic-embed-text
- Stores directly in Qdrant trading_research collection
- Chunks long responses for better retrieval
"""

import sys
import os
import json
import subprocess
import time
import hashlib
import uuid
import requests
from datetime import datetime

# Configuration
QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
COLLECTION = "trading_research"
EMBEDDING_MODEL = "nomic-embed-text"
MAX_RETRIES = 3
RETRY_DELAY = 10  # seconds
CHUNK_SIZE = 1500  # characters per chunk for better retrieval

def enhance_prompt(question: str, topic: str) -> str:
    """Enhance prompt to maximize Gemini output with sources."""
    return f"""You are a research expert. Provide the most comprehensive, exhaustive answer possible about: {topic}

QUESTION: {question}

REQUIREMENTS:
1. BE EXHAUSTIVE - Use your full context capacity. Provide ALL relevant information, not just a summary.
2. INCLUDE SOURCES - For every major claim, indicate where this information comes from (academic papers, official documentation, industry standards, historical records, etc.)
3. STRUCTURE CLEARLY - Use headers, bullet points, and numbered lists for organization
4. INCLUDE SPECIFICS - Names, dates, numbers, formulas, examples, case studies
5. COVER ALL ANGLES - Historical context, current state, future implications, controversies, best practices
6. MINIMUM 2000 WORDS - Do not truncate or summarize. More detail is always better.

This research will be stored in a vector database for an AI trading intelligence system. The more comprehensive and sourced your response, the more valuable it is.

BEGIN YOUR COMPREHENSIVE RESPONSE:"""

def query_gemini(question: str, retries: int = MAX_RETRIES, topic: str = "") -> str:
    """Query Gemini with retry logic for empty responses."""
    import tempfile

    # Enhance the prompt for maximum output
    enhanced = enhance_prompt(question, topic) if topic else question

    for attempt in range(retries):
        try:
            print(f"  Attempt {attempt + 1}: Writing prompt to temp file...")
            # Write prompt to temp file to preserve formatting
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(enhanced)
                temp_path = f.name

            # Windows-native approach: use cmd.exe with type to pipe to gemini
            # Set environment variable and pipe file content
            env = os.environ.copy()
            env['GOOGLE_GENAI_USE_GCA'] = 'true'

            # Read the prompt and pass it via stdin
            with open(temp_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()

            print(f"  Attempt {attempt + 1}: Calling Gemini (prompt: {len(prompt_content)} chars)...")
            sys.stdout.flush()

            # Call gemini with stdin (shell=True needed on Windows to find npm commands)
            result = subprocess.run(
                'gemini',
                input=prompt_content,
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout for comprehensive responses
                env=env,
                shell=True
            )
            print(f"  Attempt {attempt + 1}: Gemini returned ({len(result.stdout)} stdout, {len(result.stderr)} stderr)")
            if len(result.stdout) < 500 and len(result.stderr) > 100:
                print(f"  DEBUG stderr: {result.stderr[:500]}")

            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

            # Combine stdout and stderr (gemini outputs to both)
            response = (result.stdout + result.stderr).strip()

            # Check if response is meaningful (not just "Loaded cached credentials.")
            lines = [l for l in response.split('\n') if l.strip() and 'cached credentials' not in l.lower()]
            content = '\n'.join(lines)

            if len(content) > 50:  # Meaningful response
                print(f"  Got {len(content)} characters from Gemini")
                return content

            print(f"  Attempt {attempt + 1}: Empty or minimal response ({len(content)} chars), retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)

        except subprocess.TimeoutExpired:
            print(f"  Attempt {attempt + 1}: Timeout, retrying...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"  Attempt {attempt + 1}: Error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(RETRY_DELAY)

    return ""

def get_embedding(text: str) -> list:
    """Generate embedding using Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"  Embedding error: {e}")
        return None

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    """Split text into chunks for better retrieval."""
    # Try splitting by double newlines first
    paragraphs = text.split('\n\n')

    # If no double newlines, try single newlines
    if len(paragraphs) == 1:
        paragraphs = text.split('\n')

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # If single paragraph is too big, force split it
        if len(para) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            # Force split large paragraph
            for i in range(0, len(para), chunk_size):
                chunks.append(para[i:i+chunk_size])
        elif len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    # If still no chunks (empty text), return empty list
    if not chunks:
        if len(text) > 0:
            for i in range(0, len(text), chunk_size):
                chunks.append(text[i:i+chunk_size])

    print(f"  Chunked into {len(chunks)} pieces (sizes: {[len(c) for c in chunks[:5]]}...)")
    return chunks

def store_in_qdrant(topic: str, content: str, domain: str, tags: list, question: str) -> int:
    """Store research in Qdrant with chunking."""
    chunks = chunk_text(content)
    stored_count = 0
    timestamp = datetime.now().isoformat()

    for i, chunk in enumerate(chunks):
        # Generate unique UUID for Qdrant
        chunk_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{topic}-{i}-{timestamp}"))

        # Generate embedding
        embedding = get_embedding(chunk)
        if not embedding:
            print(f"  Failed to embed chunk {i+1}/{len(chunks)}")
            continue

        # Prepare point
        point = {
            "id": chunk_id,
            "vector": embedding,
            "payload": {
                "topic": topic,
                "domain": domain,
                "tags": tags,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "content": chunk,
                "question": question,
                "timestamp": timestamp,
                "source": "gemini"
            }
        }

        # Store in Qdrant
        try:
            response = requests.put(
                f"{QDRANT_URL}/collections/{COLLECTION}/points",
                json={"points": [point]},
                timeout=10
            )
            if response.status_code != 200:
                print(f"  Qdrant error response: {response.text}")
            response.raise_for_status()
            stored_count += 1
            print(f"  Stored chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
        except Exception as e:
            print(f"  Qdrant storage error for chunk {i+1}: {e}")

    return stored_count

def main():
    if len(sys.argv) < 4:
        print("Usage: research-to-vector.py 'topic' 'question' 'domain' ['tag1,tag2,tag3']")
        sys.exit(1)

    topic = sys.argv[1]
    question = sys.argv[2]
    domain = sys.argv[3]
    tags = sys.argv[4].split(',') if len(sys.argv) > 4 else []

    print(f"Researching: {topic}")
    print(f"  Domain: {domain}")
    print(f"  Tags: {tags}")

    # Query Gemini with enhanced prompt
    print("  Querying Gemini (enhanced prompt for max output)...")
    content = query_gemini(question, topic=topic)

    if not content:
        print("  ERROR: Failed to get response from Gemini after retries")
        sys.exit(1)

    print(f"  Got {len(content)} characters of content")

    # Store in Qdrant
    print("  Storing in Qdrant...")
    stored = store_in_qdrant(topic, content, domain, tags, question)

    print(f"  SUCCESS: Stored {stored} chunks in trading_research collection")
    print(f"STORED: {topic} ({stored} chunks)")

if __name__ == "__main__":
    main()
