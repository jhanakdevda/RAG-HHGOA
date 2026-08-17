"""
Comprehensive Dataset & Corpus Inspection Script for RAGE HH GOA 2026
"""

import os
import sys
import json
import faiss

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_all():
    print("=" * 80)
    print("PHASE 1: COMPREHENSIVE DATASET & FAISS CORPUS INSPECTION")
    print("=" * 80)

    # 1. Inspect Vector Store Index
    index_path = "vector_store/index.faiss"
    metadata_path = "vector_store/chunk_metadata.jsonl"

    if os.path.exists(index_path):
        idx = faiss.read_index(index_path)
        print(f"\n1. FAISS Index ({index_path}):")
        print(f"   - Vector Count (ntotal) : {idx.ntotal}")
        print(f"   - Vector Dimension (d)  : {idx.d}")
    else:
        print(f"\n1. FAISS Index ({index_path}) NOT FOUND.")

    # 2. Inspect Metadata File
    if os.path.exists(metadata_path):
        count = 0
        languages = set()
        goa_count = 0
        with open(metadata_path, "r", encoding="utf-8") as f:
            for line in f:
                count += 1
                obj = json.loads(line)
                languages.add(obj.get("language_code", "unknown"))
                txt = (obj.get("text") or "").lower()
                if "goa" in txt or "panaji" in txt or "panjim" in txt:
                    goa_count += 1
        print(f"\n2. Metadata File ({metadata_path}):")
        print(f"   - Chunk Record Count    : {count}")
        print(f"   - Languages Present     : {sorted(list(languages))}")
        print(f"   - Chunks with Goa/Panaji: {goa_count}")

    # 3. Inspect Processed Chunks Files
    processed_dir = "data/processed"
    print(f"\n3. Processed Datasets ({processed_dir}):")
    if os.path.exists(processed_dir):
        for fname in os.listdir(processed_dir):
            if fname.endswith(".jsonl"):
                fpath = os.path.join(processed_dir, fname)
                rec_count = 0
                goa_matches = 0
                langs = set()
                with open(fpath, "r", encoding="utf-8") as f:
                    for line in f:
                        rec_count += 1
                        obj = json.loads(line)
                        langs.add(obj.get("language_code", "unknown"))
                        txt = (obj.get("text") or "").lower()
                        if "goa" in txt or "panaji" in txt or "panjim" in txt:
                            goa_matches += 1
                print(f"   - File: {fname}")
                print(f"     * Record Count    : {rec_count}")
                print(f"     * Languages       : {sorted(list(langs))}")
                print(f"     * Goa/Panaji Match: {goa_matches}")

    # 4. Check Raw Validation Datasets (MS MARCO-XI Parquet files)
    raw_val_dir = "data/raw/validation"
    print(f"\n4. Raw Parquet Datasets ({raw_val_dir}):")
    if os.path.exists(raw_val_dir):
        p_files = [f for f in os.listdir(raw_val_dir) if f.endswith(".parquet")]
        print(f"   - Parquet Files Count: {len(p_files)}")

if __name__ == "__main__":
    inspect_all()
