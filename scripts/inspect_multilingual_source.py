"""
Official Multilingual Dataset Inspector and Sampler for AI4Bharat/MSMARCO-XI

Fetches authentic sample records directly from official ai4bharat/MSMARCO-XI validation files
across multiple target languages (hi, mr, bn, ta, ur) and saves them to data/sample/msmarco_xi_hi_sample.jsonl.
"""

import os
import json
import time
from datasets import load_dataset

OUTPUT_SAMPLE_PATH = os.path.join("data", "sample", "msmarco_xi_hi_sample.jsonl")

# Target validation files from official AI4Bharat/MSMARCO-XI Hugging Face repository
LANG_PARQUETS = [
    ("hi", "https://huggingface.co/datasets/ai4bharat/MSMARCO-XI/resolve/main/validation/hinval.parquet"),
    ("mr", "https://huggingface.co/datasets/ai4bharat/MSMARCO-XI/resolve/main/validation/marval.parquet"),
    ("bn", "https://huggingface.co/datasets/ai4bharat/MSMARCO-XI/resolve/main/validation/benval.parquet"),
    ("ta", "https://huggingface.co/datasets/ai4bharat/MSMARCO-XI/resolve/main/validation/tamval.parquet"),
    ("ur", "https://huggingface.co/datasets/ai4bharat/MSMARCO-XI/resolve/main/validation/urdval.parquet"),
]


def fetch_official_samples(samples_per_lang: int = 15):
    official_records = []
    summary_by_lang = {}

    print("=" * 60)
    print("Inspecting Official AI4Bharat MSMARCO-XI Multilingual Parquet Files")
    print("=" * 60)

    for lang_code, url in LANG_PARQUETS:
        start_t = time.time()
        print(f"\nStreaming {samples_per_lang} official records for '{lang_code}'...")

        try:
            ds = load_dataset("parquet", data_files={"train": url}, split="train", streaming=True)
            count = 0
            for item in ds:
                meta_raw = item.get("meta", {}) or {}
                passages_raw = item.get("passages", {}) or {}

                rec = {
                    "source_lang": str(item.get("source_lang") or "en"),
                    "target_lang": str(item.get("target_lang") or lang_code),
                    "query_id": int(item.get("query_id") or 0),
                    "query_type": str(item.get("query_type") or "description"),
                    "query": str(item.get("query") or ""),
                    "Answer": str(item.get("Answer") or ""),
                    "Eng_Query": str(item.get("Eng_Query") or ""),
                    "Eng_Answer": str(item.get("Eng_Answer") or ""),
                    "meta": {
                        "model_name": str(meta_raw.get("model_name") or "IndicTrans2"),
                        "temperature": float(meta_raw.get("temperature") or 0.0),
                        "max_tokens": int(meta_raw.get("max_tokens") or 512),
                        "top_p": float(meta_raw.get("top_p") or 1.0),
                        "frequency_penalty": float(meta_raw.get("frequency_penalty") or 0.0),
                        "presence_penalty": float(meta_raw.get("presence_penalty") or 0.0),
                    },
                    "passages": {
                        "English_passages": [str(p) for p in passages_raw.get("English_passages", [])],
                        "Translated_passages": [str(p) for p in passages_raw.get("Translated_passages", [])],
                        "is_selected": [int(s) for s in passages_raw.get("is_selected", [])],
                    }
                }
                official_records.append(rec)
                count += 1
                if count >= samples_per_lang:
                    break

            summary_by_lang[lang_code] = count
            print(f"  [SUCCESS] Fetched {count} authentic records for '{lang_code}' in {time.time() - start_t:.2f}s.")

        except Exception as e:
            print(f"  [ERROR] Failed for '{lang_code}': {e}")

    # Save to data/sample/msmarco_xi_hi_sample.jsonl
    os.makedirs(os.path.dirname(OUTPUT_SAMPLE_PATH), exist_ok=True)
    with open(OUTPUT_SAMPLE_PATH, "w", encoding="utf-8") as f:
        for rec in official_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("\n" + "=" * 60)
    print("Official Multilingual Sourcing Summary")
    print("=" * 60)
    print(f"  Output Path: {OUTPUT_SAMPLE_PATH}")
    print(f"  Total Authentic Records Sourced: {len(official_records)}")
    print("  Breakdown by Language:")
    for l_code, count in summary_by_lang.items():
        print(f"    - {l_code:5s}: {count} records")
    print(f"  File Size: {os.path.getsize(OUTPUT_SAMPLE_PATH) / 1024:.2f} KB")
    print("=" * 60)

    return official_records


if __name__ == "__main__":
    fetch_official_samples(15)
