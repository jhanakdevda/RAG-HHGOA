"""
Inspect topics and text passages present in the active 300-chunk vector index
"""

import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_corpus():
    metadata_path = "vector_store/chunk_metadata.jsonl"
    print("=" * 80)
    print(f"Inspecting active vector store metadata: {metadata_path}")
    print("=" * 80)

    topics = set()
    sample_queries = []

    with open(metadata_path, "r", encoding="utf-8") as f:
        for line in f:
            chunk = json.loads(line)
            query_id = chunk.get("query_id")
            text = chunk.get("text", "")
            lang = chunk.get("language_code", "")

            if query_id not in topics:
                topics.add(query_id)
                sample_queries.append({"query_id": query_id, "lang": lang, "snippet": text[:100]})

    print(f"Total Unique Query Topics in Index: {len(topics)}")
    print("\nSample Topic Passages Present in Vector Store:")
    for i, s in enumerate(sample_queries[:15]):
        print(f"  {i+1}. Query #{s['query_id']} [{s['lang']}]: '{s['snippet']}...'")

if __name__ == "__main__":
    inspect_corpus()
