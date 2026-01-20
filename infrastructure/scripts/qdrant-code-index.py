#!/usr/bin/env python3
"""
qdrant-code-index.py - Index Python code in Qdrant for semantic search

Parses Python files using AST, extracts functions and classes,
embeds them with Ollama, and stores to Qdrant.

Usage:
  python qdrant-code-index.py --path /path/to/project --collection code_index
  python qdrant-code-index.py --path . --collection code_index --exclude "venv,node_modules"

Features:
  - Extracts functions and classes with docstrings
  - Tracks commit hash to avoid re-indexing
  - Embeds code + docstring for semantic search
  - Excludes generated code, dependencies
"""

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_DIM = 768

# Default exclusions
DEFAULT_EXCLUDES = {
    "venv", "env", ".venv", "__pycache__", "node_modules",
    ".git", "build", "dist", "*.egg-info", ".tox", ".mypy_cache"
}


def get_git_commit_hash(path):
    """Get current git commit hash for the repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]  # Short hash
    except Exception:
        pass
    return "unknown"


def get_file_hash(file_path):
    """Get hash of file contents for change detection."""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:12]


def get_ollama_embedding(text, model="nomic-embed-text"):
    """Get embedding from local Ollama instance."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": model, "prompt": text[:8000]},
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            embedding = data.get("embedding", [])
            if embedding and len(embedding) == EMBEDDING_DIM:
                return embedding
    except Exception as e:
        print(f"Ollama error: {e}", file=sys.stderr)
    return None


def get_hash_embedding(text):
    """Fallback: deterministic pseudo-embedding from hash."""
    text_hash = hashlib.sha256(text.encode('utf-8', errors='replace')).hexdigest()
    embedding = []
    for i in range(EMBEDDING_DIM):
        hash_segment = int(text_hash[(i * 2) % 64:(i * 2) % 64 + 2], 16)
        embedding.append((hash_segment / 255.0) * 2 - 1)
    return embedding


def ensure_collection_exists(collection):
    """Create collection if it doesn't exist."""
    response = requests.get(f"{QDRANT_URL}/collections/{collection}")
    if response.status_code == 200:
        return True

    create_response = requests.put(
        f"{QDRANT_URL}/collections/{collection}",
        json={
            "vectors": {
                "size": EMBEDDING_DIM,
                "distance": "Cosine"
            }
        }
    )
    return create_response.status_code == 200


def ensure_payload_indexes(collection):
    """Create payload indexes for efficient filtering."""
    indexes = [
        ("type", "keyword"),
        ("kind", "keyword"),
        ("name", "keyword"),
        ("file_path", "keyword"),
        ("commit_hash", "keyword"),
    ]

    for field, field_type in indexes:
        try:
            requests.put(
                f"{QDRANT_URL}/collections/{collection}/index",
                json={
                    "field_name": field,
                    "field_schema": field_type
                }
            )
        except:
            pass


def store_points_batch(collection, points):
    """Store multiple points in a single Qdrant API call."""
    url = f"{QDRANT_URL}/collections/{collection}/points"

    data = {
        "points": [
            {
                "id": p["id"],
                "vector": p["vector"],
                "payload": p["payload"]
            }
            for p in points
        ]
    }

    response = requests.put(url, json=data, headers={"Content-Type": "application/json"})
    return response.json()


def get_indexed_file_hashes(collection):
    """Get all indexed file hashes to detect changes."""
    hashes = {}
    try:
        response = requests.post(
            f"{QDRANT_URL}/collections/{collection}/points/scroll",
            json={
                "limit": 10000,
                "with_payload": ["file_path", "file_hash"]
            }
        )
        if response.status_code == 200:
            result = response.json().get("result", {})
            for point in result.get("points", []):
                payload = point.get("payload", {})
                file_path = payload.get("file_path")
                file_hash = payload.get("file_hash")
                if file_path and file_hash:
                    hashes[file_path] = file_hash
    except Exception as e:
        print(f"Error getting indexed hashes: {e}", file=sys.stderr)
    return hashes


def delete_file_points(collection, file_path):
    """Delete all points for a file (before re-indexing)."""
    try:
        requests.post(
            f"{QDRANT_URL}/collections/{collection}/points/delete",
            json={
                "filter": {
                    "must": [
                        {"key": "file_path", "match": {"value": file_path}}
                    ]
                }
            }
        )
    except Exception as e:
        print(f"Error deleting points for {file_path}: {e}", file=sys.stderr)


class CodeExtractor(ast.NodeVisitor):
    """Extract functions and classes from Python AST."""

    def __init__(self, source_code, file_path):
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.file_path = file_path
        self.extracts = []
        self.imports = []
        self.module_docstring = None

    def get_source_segment(self, node):
        """Get source code for a node."""
        try:
            return ast.get_source_segment(self.source_code, node)
        except:
            # Fallback to line-based extraction
            start = node.lineno - 1
            end = node.end_lineno if hasattr(node, 'end_lineno') else start + 1
            return '\n'.join(self.source_lines[start:end])

    def visit_Import(self, node):
        """Track imports."""
        for alias in node.names:
            self.imports.append(f"import {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Track from imports."""
        module = node.module or ''
        names = ', '.join(alias.name for alias in node.names)
        self.imports.append(f"from {module} import {names}")
        self.generic_visit(node)

    def visit_Module(self, node):
        """Extract module docstring."""
        self.module_docstring = ast.get_docstring(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Extract function definitions."""
        self._extract_function(node, "function")
        # Don't visit nested functions
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.visit(child)

    def visit_AsyncFunctionDef(self, node):
        """Extract async function definitions."""
        self._extract_function(node, "async_function")
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.visit(child)

    def _extract_function(self, node, kind):
        """Extract function details."""
        # Skip private functions (single underscore) and magic methods
        if node.name.startswith('_') and not node.name.startswith('__'):
            return
        if node.name.startswith('__') and node.name.endswith('__'):
            # Only include __init__ for classes
            if node.name != '__init__':
                return

        docstring = ast.get_docstring(node) or ""
        source = self.get_source_segment(node)

        # Build signature
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                try:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                except:
                    pass
            args.append(arg_str)

        returns = ""
        if node.returns:
            try:
                returns = f" -> {ast.unparse(node.returns)}"
            except:
                pass

        signature = f"def {node.name}({', '.join(args)}){returns}:"

        self.extracts.append({
            "name": node.name,
            "kind": kind,
            "docstring": docstring,
            "signature": signature,
            "code": source,
            "line_start": node.lineno,
            "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
        })

    def visit_ClassDef(self, node):
        """Extract class definitions."""
        # Skip private classes
        if node.name.startswith('_'):
            return

        docstring = ast.get_docstring(node) or ""
        source = self.get_source_segment(node)

        # Build bases
        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except:
                pass

        bases_str = f"({', '.join(bases)})" if bases else ""
        signature = f"class {node.name}{bases_str}:"

        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_doc = ast.get_docstring(item) or ""
                methods.append({
                    "name": item.name,
                    "docstring": method_doc[:200]  # Truncate for summary
                })

        self.extracts.append({
            "name": node.name,
            "kind": "class",
            "docstring": docstring,
            "signature": signature,
            "code": source,
            "line_start": node.lineno,
            "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
            "methods": methods
        })

        # Also visit methods
        self.generic_visit(node)


def extract_from_file(file_path):
    """Extract functions and classes from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            source = f.read()

        tree = ast.parse(source)
        extractor = CodeExtractor(source, file_path)
        extractor.visit(tree)

        return {
            "imports": extractor.imports,
            "module_docstring": extractor.module_docstring,
            "extracts": extractor.extracts
        }
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return None


def should_exclude(path, excludes):
    """Check if path should be excluded."""
    path_parts = Path(path).parts
    for part in path_parts:
        if part in excludes:
            return True
        # Check glob patterns
        for exclude in excludes:
            if '*' in exclude:
                import fnmatch
                if fnmatch.fnmatch(part, exclude):
                    return True
    return False


def find_python_files(root_path, excludes):
    """Find all Python files in path, excluding specified directories."""
    python_files = []
    root = Path(root_path)

    for path in root.rglob("*.py"):
        rel_path = path.relative_to(root)
        if not should_exclude(str(rel_path), excludes):
            python_files.append(path)

    return python_files


def main():
    parser = argparse.ArgumentParser(description="Index Python code in Qdrant")
    parser.add_argument("--path", required=True, help="Path to project root")
    parser.add_argument("--collection", default="code_index", help="Qdrant collection name")
    parser.add_argument("--exclude", default="", help="Comma-separated list of dirs to exclude")
    parser.add_argument("--force", action="store_true", help="Force re-index all files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be indexed")

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}")
        sys.exit(1)

    # Build exclusions
    excludes = DEFAULT_EXCLUDES.copy()
    if args.exclude:
        excludes.update(e.strip() for e in args.exclude.split(","))

    # Get commit hash
    commit_hash = get_git_commit_hash(root_path)

    # Find Python files
    python_files = find_python_files(root_path, excludes)
    print(f"Found {len(python_files)} Python files")

    if args.dry_run:
        for f in python_files:
            print(f"  {f.relative_to(root_path)}")
        return

    # Ensure collection exists
    ensure_collection_exists(args.collection)
    ensure_payload_indexes(args.collection)

    # Get existing file hashes for incremental indexing
    indexed_hashes = {} if args.force else get_indexed_file_hashes(args.collection)

    # Process files
    files_to_index = []
    for file_path in python_files:
        rel_path = str(file_path.relative_to(root_path))
        current_hash = get_file_hash(file_path)

        if not args.force and indexed_hashes.get(rel_path) == current_hash:
            continue  # Skip unchanged files

        files_to_index.append((file_path, rel_path, current_hash))

    print(f"Indexing {len(files_to_index)} new/changed files...")

    # Extract code items first
    all_items = []
    timestamp = int(datetime.now().timestamp())

    for file_path, rel_path, file_hash in files_to_index:
        # Delete old points for this file
        delete_file_points(args.collection, rel_path)

        # Extract code
        result = extract_from_file(file_path)
        if not result:
            continue

        imports = result["imports"]
        module_doc = result["module_docstring"] or ""

        for extract in result["extracts"]:
            # Build embedding text: signature + docstring + code preview
            embed_parts = [
                extract["signature"],
                extract["docstring"],
                extract["code"][:1000]  # First 1000 chars of code
            ]
            embed_text = "\n\n".join(p for p in embed_parts if p)

            payload = {
                "type": "code",
                "kind": extract["kind"],
                "name": extract["name"],
                "file_path": rel_path,
                "file_hash": file_hash,
                "line_start": extract["line_start"],
                "line_end": extract["line_end"],
                "signature": extract["signature"],
                "docstring": extract["docstring"],
                "code": extract["code"],
                "imports": imports[:10],  # Top 10 imports
                "module_docstring": module_doc[:500],
                "commit_hash": commit_hash,
                "timestamp": timestamp
            }

            # Add methods for classes
            if extract["kind"] == "class" and "methods" in extract:
                payload["methods"] = extract["methods"]

            all_items.append({
                "embed_text": embed_text,
                "payload": payload
            })

    print(f"Generating embeddings for {len(all_items)} code items...")

    # Parallel embedding with ThreadPoolExecutor (L01 optimization)
    def embed_item(item_data):
        """Generate embedding for a single code item."""
        idx, item = item_data
        embedding = get_ollama_embedding(item["embed_text"])
        if not embedding:
            return idx, get_hash_embedding(item["embed_text"]), "hash"
        return idx, embedding, "ollama"

    embeddings = [None] * len(all_items)
    optimal_workers = min(len(all_items), 32)

    with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
        futures = {executor.submit(embed_item, (i, item)): i for i, item in enumerate(all_items)}
        for future in as_completed(futures):
            idx, embedding, source = future.result()
            embeddings[idx] = embedding
            if source == "hash":
                print(f"Warning: Using hash fallback for item {idx}", file=sys.stderr)

    # Build points with embeddings
    all_points = []
    for i, item in enumerate(all_items):
        all_points.append({
            "id": str(uuid.uuid4()),
            "vector": embeddings[i],
            "payload": item["payload"]
        })

    # Batch store
    if all_points:
        # Store in batches of 100
        batch_size = 100
        for i in range(0, len(all_points), batch_size):
            batch = all_points[i:i+batch_size]
            result = store_points_batch(args.collection, batch)
            if result.get("status") != "ok":
                print(f"Warning: Batch store issue: {result}", file=sys.stderr)

    # Report results
    print(json.dumps({
        "success": True,
        "files_processed": len(files_to_index),
        "items_indexed": len(all_points),
        "commit_hash": commit_hash,
        "collection": args.collection
    }, indent=2))


if __name__ == "__main__":
    main()
