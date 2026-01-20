#!/usr/bin/env python3
# qdrant-query.py

import argparse
import json
import sys
import requests

# --- Configuration ---
QDRANT_URL = "http://localhost:6333"
# Set a reasonable limit for each scroll request. The script will paginate automatically.
SCROLL_LIMIT = 50

def query_qdrant(collection: str, filter_payload: dict) -> list:
    """
    Queries the Qdrant collection using the scroll API to retrieve all matching documents.

    Args:
        collection: The name of the collection to query.
        filter_payload: The filter conditions to apply to the search.

    Returns:
        A list of all found points (documents).
    """
    all_points = []
    next_page_offset = None
    headers = {'Content-Type': 'application/json'}

    while True:
        payload = {
            "filter": filter_payload,
            "limit": SCROLL_LIMIT,
            "with_payload": True
        }
        if next_page_offset:
            payload["offset"] = next_page_offset

        scroll_url = f"{QDRANT_URL}/collections/{collection}/points/scroll"

        try:
            response = requests.post(scroll_url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

            data = response.json()
            result = data.get('result', {})
            all_points.extend(result.get('points', []))

            next_page_offset = result.get('next_page_offset')
            if not next_page_offset:
                break  # Exit loop if there are no more pages

        except requests.exceptions.ConnectionError:
            print(f"Error: Connection to Qdrant at {QDRANT_URL} refused. Is Qdrant running?", file=sys.stderr)
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print(f"Error: An HTTP error occurred: {e}", file=sys.stderr)
            print(f"Response body: {e.response.text}", file=sys.stderr)
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Error: A request error occurred: {e}", file=sys.stderr)
            sys.exit(1)

    return all_points

def format_as_text(results: list):
    """Formats and prints the query results in a human-readable text format."""
    if not results:
        print("No documents found matching the criteria.")
        return

    print(f"Found {len(results)} document(s).\n")
    for i, point in enumerate(results):
        print(f"--- Document {i+1}/{len(results)} ---")
        print(f"  id: {point.get('id')}")
        payload = point.get('payload', {})
        for key, value in payload.items():
            print(f"  {key}: {value}")
        print("-" * (18 + len(str(i+1)) + len(str(len(results)))))
        print()

def format_as_json(results: list):
    """Formats and prints the query results as a JSON array."""
    print(json.dumps(results, indent=2))

def main():
    """Main function to parse arguments and orchestrate the query."""
    parser = argparse.ArgumentParser(
        description="A CLI script to query a Qdrant instance using the 'requests' library.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--collection",
        type=str,
        required=True,
        help="Name of the Qdrant collection to query (e.g., 'lineage_research')."
    )

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--output",
        type=str,
        choices=['text', 'json'],
        default='text',
        help="The output format for the results. Defaults to 'text'."
    )

    # A group for mutually exclusive search modes
    search_mode_group = parser.add_mutually_exclusive_group(required=True)
    search_mode_group.add_argument(
        "--topic",
        type=str,
        help="Search for an exact topic name."
    )
    search_mode_group.add_argument(
        "--tags",
        nargs='+',
        help="Search for documents with ANY of the given tags (e.g., --tags python qdrant)."
    )
    search_mode_group.add_argument(
        "--list-all",
        action='store_true',
        help="List all documents in the specified collection."
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    qdrant_filter = {}

    if args.topic:
        qdrant_filter = {
            "must": [
                {"key": "topic", "match": {"value": args.topic}}
            ]
        }
    elif args.tags:
        qdrant_filter = {
            "must": [
                {"key": "tags", "match": {"any": args.tags}}
            ]
        }
    elif args.list_all:
        # No filter needed, retrieves all documents
        qdrant_filter = {}

    results = query_qdrant(args.collection, qdrant_filter)

    if args.output == 'json':
        format_as_json(results)
    else:
        format_as_text(results)

if __name__ == "__main__":
    main()
