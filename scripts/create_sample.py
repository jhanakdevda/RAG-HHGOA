"""
Authentic Multilingual Sample Extractor for MS MARCO-XI

Reads authentic records directly from downloaded official MSMARCO-XI validation Parquet files
in data/raw/validation/ across all 14 target languages (as, bn, gu, hi, kn, ml, mr, ne, or, pa, sa, ta, te, ur)
and outputs data/sample/msmarco_xi_multilingual_sample.jsonl.
"""

import os
import sys
import json
import pyarrow.parquet as pq
from typing import List, Dict

# Force UTF-8 encoding for standard output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_VAL_DIR = os.path.join("data", "raw", "validation")
OUTPUT_SAMPLE_PATH = os.path.join("data", "sample", "msmarco_xi_multilingual_sample.jsonl")

LANGUAGE_MAP: List[Dict[str, str]] = [
    {"code": "as", "name": "Assamese", "file": "asmval.parquet"},
    {"code": "bn", "name": "Bengali", "file": "benval.parquet"},
    {"code": "gu", "name": "Gujarati", "file": "gujval.parquet"},
    {"code": "hi", "name": "Hindi", "file": "hinval.parquet"},
    {"code": "kn", "name": "Kannada", "file": "kanval.parquet"},
    {"code": "ml", "name": "Malayalam", "file": "malval.parquet"},
    {"code": "mr", "name": "Marathi", "file": "marval.parquet"},
    {"code": "ne", "name": "Nepali", "file": "nepval.parquet"},
    {"code": "or", "name": "Odia", "file": "orival.parquet"},
    {"code": "pa", "name": "Punjabi", "file": "panval.parquet"},
    {"code": "sa", "name": "Sanskrit", "file": "sanval.parquet"},
    {"code": "ta", "name": "Tamil", "file": "tamval.parquet"},
    {"code": "te", "name": "Telugu", "file": "telval.parquet"},
    {"code": "ur", "name": "Urdu", "file": "urdval.parquet"},
]


def extract_authentic_samples(records_per_lang: int = 20):
    if not os.path.exists(RAW_VAL_DIR):
        print(f"Error: Raw validation directory '{RAW_VAL_DIR}' does not exist. Run scripts/download_dataset.py first.")
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_SAMPLE_PATH), exist_ok=True)
    all_authentic_records = []
    summary_by_lang = {}

    print("=" * 70)
    print("Extracting Authentic Sample Records from Local data/raw/validation/*.parquet")
    print("=" * 70)

    for lang in LANGUAGE_MAP:
        code = lang["code"]
        name = lang["name"]
        file_name = lang["file"]
        file_path = os.path.join(RAW_VAL_DIR, file_name)

        if not os.path.exists(file_path):
            print(f"Warning: File '{file_path}' missing. Skipping {name}.")
            continue

        print(f"Reading authentic records for {name:10s} ({code}) from {file_name}...")
        pf = pq.ParquetFile(file_path)
        rg0 = pf.read_row_group(0)
        slice_data = rg0.slice(0, records_per_lang).to_pydict()

        num_rows = len(slice_data["query_id"])
        summary_by_lang[name] = num_rows

        for i in range(num_rows):
            meta_raw = slice_data["meta"][i] if "meta" in slice_data else {}
            passages_raw = slice_data["passages"][i] if "passages" in slice_data else {}

            rec = {
                "source_lang": str(slice_data.get("source_lang", ["en"] * num_rows)[i]),
                "target_lang": str(slice_data.get("target_lang", [code] * num_rows)[i]),
                "language_name": name,
                "query_id": int(slice_data["query_id"][i]),
                "query_type": str(slice_data.get("query_type", ["description"] * num_rows)[i]),
                "query": str(slice_data["query"][i]),
                "Answer": str(slice_data.get("Answer", [""] * num_rows)[i]),
                "Eng_Query": str(slice_data.get("Eng_Query", [""] * num_rows)[i]),
                "Eng_Answer": str(slice_data.get("Eng_Answer", [""] * num_rows)[i]),
                "meta": {
                    "model_name": str(meta_raw.get("model_name", "IndicTrans2")),
                    "temperature": float(meta_raw.get("temperature", 0.0)),
                    "max_tokens": int(meta_raw.get("max_tokens", 512)),
                    "top_p": float(meta_raw.get("top_p", 1.0)),
                    "frequency_penalty": float(meta_raw.get("frequency_penalty", 0.0)),
                    "presence_penalty": float(meta_raw.get("presence_penalty", 0.0)),
                },
                "passages": {
                    "English_passages": [str(p) for p in passages_raw.get("English_passages", [])],
                    "Translated_passages": [str(p) for p in passages_raw.get("Translated_passages", [])],
                    "is_selected": [int(s) for s in passages_raw.get("is_selected", [])],
                },
            }
            all_authentic_records.append(rec)

    # Save to data/sample/msmarco_xi_multilingual_sample.jsonl
    with open(OUTPUT_SAMPLE_PATH, "w", encoding="utf-8") as f:
        for rec in all_authentic_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    out_kb = os.path.getsize(OUTPUT_SAMPLE_PATH) / 1024

    print("\n" + "=" * 70)
    print("Authentic Multilingual Sample Summary")
    print("=" * 70)
    print(f"  Output Sample File       : {OUTPUT_SAMPLE_PATH}")
    print(f"  Total Authentic Records  : {len(all_authentic_records)}")
    print(f"  Languages Represented    : {len(summary_by_lang)}")
    print(f"  File Size                : {out_kb:.2f} KB")
    print("\n  Extracted Breakdown by Language:")
    for lname, count in summary_by_lang.items():
        print(f"    - {lname:12s}: {count} authentic records")
    print("=" * 70)

    return all_authentic_records


if __name__ == "__main__":
    extract_authentic_samples(20)
