"""
Official MSMARCO-XI Dataset Downloader (AI4Bharat/MSMARCO-XI)

Downloads all 14 official validation Parquet files from huggingface.co/datasets/ai4bharat/MSMARCO-XI
into data/raw/ and verifies each file's size and total row count.
Does NOT download the 45.67 GB train split.
"""

import os
import sys
import time
from huggingface_hub import hf_hub_download
import pyarrow.parquet as pq

# Force UTF-8 encoding for standard output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ID = "ai4bharat/MSMARCO-XI"
RAW_DIR = os.path.join("data", "raw")

# 14 official target language validation Parquet files
VALIDATION_FILES = [
    ("as", "Assamese", "asmval.parquet"),
    ("bn", "Bengali", "benval.parquet"),
    ("gu", "Gujarati", "gujval.parquet"),
    ("hi", "Hindi", "hinval.parquet"),
    ("kn", "Kannada", "kanval.parquet"),
    ("ml", "Malayalam", "malval.parquet"),
    ("mr", "Marathi", "marval.parquet"),
    ("ne", "Nepali", "nepval.parquet"),
    ("or", "Odia", "orival.parquet"),
    ("pa", "Punjabi", "panval.parquet"),
    ("sa", "Sanskrit", "sanval.parquet"),
    ("ta", "Tamil", "tamval.parquet"),
    ("te", "Telugu", "telval.parquet"),
    ("ur", "Urdu", "urdval.parquet"),
]


def download_validation_dataset():
    os.makedirs(RAW_DIR, exist_ok=True)

    print("=" * 70)
    print("Official AI4Bharat/MSMARCO-XI Validation Dataset Downloader")
    print("=" * 70)
    print(f"Target Directory : {RAW_DIR}")
    print(f"Total Languages  : {len(VALIDATION_FILES)}")
    print("=" * 70)

    download_summary = []
    total_download_bytes = 0
    total_authentic_records = 0

    for lang_code, lang_name, file_name in VALIDATION_FILES:
        repo_filename = f"validation/{file_name}"
        dest_path = os.path.join(RAW_DIR, file_name)

        print(f"\nDownloading '{lang_name}' ({lang_code}) -> {file_name}...")
        start_t = time.time()

        try:
            downloaded_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=repo_filename,
                repo_type="dataset",
                local_dir=RAW_DIR,
            )

            # Verification: Inspect Parquet file metadata
            file_size = os.path.getsize(downloaded_path)
            pf = pq.ParquetFile(downloaded_path)
            num_rows = pf.metadata.num_rows

            duration = time.time() - start_t
            size_mb = file_size / (1024 * 1024)

            total_download_bytes += file_size
            total_authentic_records += num_rows

            download_summary.append({
                "lang_code": lang_code,
                "lang_name": lang_name,
                "file_name": file_name,
                "size_mb": size_mb,
                "num_rows": num_rows,
                "duration_s": duration
            })

            print(f"  [VERIFIED] Size: {size_mb:.2f} MB | Rows: {num_rows:,d} | Time: {duration:.2f}s")

        except Exception as e:
            print(f"  [ERROR] Failed to download {file_name}: {e}")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("Dataset Download & Verification Summary")
    print("=" * 70)
    print(f"  Total Files Downloaded   : {len(download_summary)}")
    print(f"  Total Size Downloaded    : {total_download_bytes / (1024 * 1024):.2f} MB ({total_download_bytes / (1024 * 1024 * 1024):.2f} GB)")
    print(f"  Total Authentic Records  : {total_authentic_records:,d}")
    print(f"  Train Split Downloaded   : NO (0 bytes)")
    print("\n  Per-Language Download Breakdown:")
    for item in download_summary:
        print(f"    - {item['lang_code']:2s} ({item['lang_name']:10s}): {item['size_mb']:6.2f} MB | {item['num_rows']:>7,d} records | {item['file_name']}")
    print("=" * 70)

    return download_summary


if __name__ == "__main__":
    download_validation_dataset()
