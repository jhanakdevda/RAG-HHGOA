"""
Process Dataset Chunks — Batch processing script for authentic MSMARCO-XI dataset

Reads authentic records from data/sample/msmarco_xi_multilingual_sample.jsonl,
applies AdaptiveSemanticChunker across all 14 target languages,
and writes chunk records to data/processed/msmarco_xi_multilingual_chunks.jsonl.
"""

import os
import sys
import json

# Add backend directory to python path for importing app packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.dataset import MSMarcoExample, LANGUAGE_NAME_MAP
from app.rag.chunker import AdaptiveSemanticChunker

INPUT_PATH = os.path.join("data", "sample", "msmarco_xi_multilingual_sample.jsonl")
OUTPUT_PATH = os.path.join("data", "processed", "msmarco_xi_multilingual_chunks.jsonl")


def process_chunks():
    if not os.path.isfile(INPUT_PATH):
        print(f"Error: Input file '{INPUT_PATH}' does not exist. Run scripts/create_sample.py first.")
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    chunker = AdaptiveSemanticChunker(target_chunk_size=300, max_chunk_size=500, overlap_sentences=1)

    total_examples = 0
    total_passages = 0
    all_chunks = []
    selected_chunks = 0
    languages_seen = set()

    print(f"Processing authentic sample records from '{INPUT_PATH}'...")
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            example = MSMarcoExample(**data)
            total_examples += 1
            total_passages += len(example.passages.Translated_passages)

            chunks = chunker.chunk_example(example)
            for c in chunks:
                all_chunks.append(c)
                if c.language_code:
                    languages_seen.add(c.language_code)
                if c.is_selected == 1:
                    selected_chunks += 1

    # Write output to JSONL
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out_f:
        for chunk in all_chunks:
            out_f.write(json.dumps(chunk.model_dump(), ensure_ascii=False) + "\n")

    avg_chars = sum(c.char_count for c in all_chunks) / len(all_chunks) if all_chunks else 0
    avg_words = sum(c.word_count for c in all_chunks) / len(all_chunks) if all_chunks else 0
    out_size_kb = os.path.getsize(OUTPUT_PATH) / 1024

    print("=" * 70)
    print("Multilingual Chunk Processing Summary")
    print("=" * 70)
    print(f"  Input file              : {INPUT_PATH}")
    print(f"  Output file             : {OUTPUT_PATH}")
    print(f"  Total Examples Processed: {total_examples}")
    print(f"  Total Passages Chunked  : {total_passages}")
    print(f"  Total Text Chunks Built : {len(all_chunks)}")
    print(f"  Selected Relevant Chunks: {selected_chunks}")
    print(f"  Languages Represented   : {len(languages_seen)} ({', '.join(sorted(languages_seen))})")
    print(f"  Avg Chunk Length (chars): {avg_chars:.1f}")
    print(f"  Avg Chunk Length (words): {avg_words:.1f}")
    print(f"  Output File Size        : {out_size_kb:.2f} KB")
    print("=" * 70)

    return all_chunks


if __name__ == "__main__":
    process_chunks()
