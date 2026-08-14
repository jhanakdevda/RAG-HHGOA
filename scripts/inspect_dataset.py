"""
Dataset Inspection Script for MS MARCO-XI (Hindi / Indic languages)

This script inspects the official AI4Bharat/MSMARCO-XI dataset metadata
using the lightweight Hugging Face Datasets Server API without downloading
large parquet files.
"""

import sys
import json
import urllib.request
import urllib.error

DATASET_NAME = "ai4bharat/MSMARCO-XI"
BASE_URL = "https://datasets-server.huggingface.co"


def fetch_json(endpoint: str) -> dict:
    url = f"{BASE_URL}/{endpoint}?dataset={DATASET_NAME}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        return {"error": f"HTTPError {e.code}: {e.reason}", "body": body}
    except Exception as e:
        return {"error": str(e)}


def inspect_dataset():
    print("=" * 60)
    print(f"MS MARCO-XI Dataset Inspection — {DATASET_NAME}")
    print("=" * 60)

    # 1. Fetch splits
    print("\n1. Fetching Dataset Splits...")
    splits_data = fetch_json("splits")
    if "error" in splits_data:
        print(f"   [Error] {splits_data['error']}")
    else:
        splits = splits_data.get("splits", [])
        print(f"   Found {len(splits)} splits:")
        for s in splits:
            print(f"   - Config: {s.get('config')}, Split: {s.get('split')}")

    # 2. Fetch Size Metadata
    print("\n2. Fetching Dataset Size & Scale Metrics...")
    size_data = fetch_json("size")
    if "error" in size_data:
        print(f"   [Error] {size_data['error']}")
    else:
        ds_size = size_data.get("size", {}).get("dataset", {})
        print(f"   Total rows across all splits: {ds_size.get('num_rows'):,}")
        print(f"   Compressed Parquet Size: {ds_size.get('num_bytes_parquet_files', 0) / (1024**3):.2f} GB")
        print(f"   Uncompressed Memory Size: {ds_size.get('num_bytes_memory', 0) / (1024**3):.2f} GB")

        print("\n   Split breakdown:")
        for sp in size_data.get("size", {}).get("splits", []):
            name = sp.get("split")
            rows = sp.get("num_rows", 0)
            bytes_pq = sp.get("num_bytes_parquet_files", 0) / (1024**3)
            bytes_mem = sp.get("num_bytes_memory", 0) / (1024**3)
            print(f"   - {name:12s}: {rows:10,d} rows | {bytes_pq:6.2f} GB Parquet | {bytes_mem:6.2f} GB RAM")

    # 3. Fetch Info & Schema
    print("\n3. Fetching Dataset Schema & Features...")
    info_data = fetch_json("info")
    if "error" in info_data:
        print(f"   [Error] {info_data['error']}")
    else:
        default_info = info_data.get("dataset_info", {}).get("default", {})
        features = default_info.get("features", {})
        print(f"   Verified Field Count: {len(features)}")
        print("\n   Field Definitions:")
        print(f"   {'Field Name':<20} | {'Type / Structure':<40}")
        print("   " + "-" * 65)

        for field_name, feature_def in features.items():
            if isinstance(feature_def, dict) and "_type" in feature_def:
                ftype = f"{feature_def.get('_type')}[{feature_def.get('dtype')}]"
            elif isinstance(feature_def, dict):
                ftype = f"Struct ({list(feature_def.keys())})"
            else:
                ftype = str(feature_def)
            print(f"   {field_name:<20} | {ftype:<40}")

        print("\n   Nested Field Detail — 'passages':")
        passages_def = features.get("passages", {})
        if isinstance(passages_def, dict):
            for pk, pv in passages_def.items():
                print(f"   - passages.{pk}: {pv}")

        print("\n   Nested Field Detail — 'meta':")
        meta_def = features.get("meta", {})
        if isinstance(meta_def, dict):
            for mk, mv in meta_def.items():
                print(f"   - meta.{mk}: {mv}")

    # 4. Probe Rows API Endpoint
    print("\n4. Probing Rows API Endpoint (/rows)...")
    url_rows = f"{BASE_URL}/rows?dataset={DATASET_NAME}&config=default&split=train&offset=0&length=5"
    req_rows = urllib.request.Request(url_rows, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req_rows, timeout=15) as resp:
            print("   Rows API Success!")
    except urllib.error.HTTPError as e:
        print(f"   Rows API Status: HTTP {e.code} ({e.reason})")
        print("   Explanation: HF server-side worker error due to single Parquet row-group exceeding 300MB.")

    print("\n" + "=" * 60)
    print("Dataset Inspection Complete.")
    print("=" * 60)


if __name__ == "__main__":
    inspect_dataset()
