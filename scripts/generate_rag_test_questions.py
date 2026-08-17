"""
Dataset-Based RAG Test Question Generator (Task 2 Audit & Testing Utility)

Extracts real queries and ground-truth answers directly from the indexed MS MARCO-XI dataset
(data/sample/msmarco_xi_expanded_sample.jsonl & vector_store/chunk_metadata.jsonl).

Produces a clean, numbered list of test questions for manual entry into the RAGE HH GOA frontend,
along with expected ground-truth answers, query IDs, source passages, and recommended testing order.

DOES NOT modify backend code, FAISS vector index, frontend UI, .env, or RAG pipeline logic.
"""

import os
import sys
import json
from collections import defaultdict

# Ensure UTF-8 output formatting for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Dataset File Paths
DATASET_SAMPLE_PATH = os.path.join("data", "sample", "msmarco_xi_expanded_sample.jsonl")
FAISS_METADATA_PATH = os.path.join("vector_store", "chunk_metadata.jsonl")

# Language display mapping
LANG_DISPLAY = {
    "en": "English",
    "English": "English",
    "hi": "Hindi",
    "Hindi": "Hindi",
    "mr": "Marathi",
    "Marathi": "Marathi",
    "bn": "Bengali",
    "Bengali": "Bengali",
    "ta": "Tamil",
    "Tamil": "Tamil",
    "te": "Telugu",
    "Telugu": "Telugu",
    "gu": "Gujarati",
    "Gujarati": "Gujarati",
    "kn": "Kannada",
    "Kannada": "Kannada",
    "ml": "Malayalam",
    "Malayalam": "Malayalam",
    "pa": "Punjabi",
    "Punjabi": "Punjabi",
    "or": "Odia",
    "Odia": "Odia",
    "ur": "Urdu",
    "Urdu": "Urdu",
    "as": "Assamese",
    "Assamese": "Assamese",
    "ne": "Nepali",
    "Nepali": "Nepali",
    "sa": "Sanskrit",
    "Sanskrit": "Sanskrit"
}


def load_indexed_query_ids():
    """Loads all unique query_ids indexed in the FAISS vector store."""
    indexed_qids = set()
    if os.path.exists(FAISS_METADATA_PATH):
        with open(FAISS_METADATA_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    if "query_id" in rec:
                        indexed_qids.add(rec["query_id"])
                except Exception:
                    pass
    return indexed_qids


def load_dataset_records(indexed_qids):
    """Loads records from msmarco_xi_expanded_sample.jsonl matching indexed query_ids."""
    records_by_lang = defaultdict(list)
    all_found_langs = set()

    if not os.path.exists(DATASET_SAMPLE_PATH):
        print(f"Error: Dataset file not found at {DATASET_SAMPLE_PATH}")
        return records_by_lang, all_found_langs

    with open(DATASET_SAMPLE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                qid = rec.get("query_id")

                # Ensure query_id is present in indexed FAISS store if loaded
                if indexed_qids and qid not in indexed_qids:
                    continue

                lang_name = rec.get("language_name") or rec.get("target_lang") or "Unknown"
                all_found_langs.add(lang_name)

                query = rec.get("query", "").strip().lstrip(".? ").strip()
                ans = rec.get("Answer", "").strip()
                eng_query = rec.get("Eng_Query", "").strip().lstrip(".? ").strip()
                eng_ans = rec.get("Eng_Answer", "").strip()

                # Capitalize English query cleanly
                if eng_query:
                    eng_query = eng_query[0].upper() + eng_query[1:]

                rec["query"] = query
                rec["Answer"] = ans
                rec["Eng_Query"] = eng_query
                rec["Eng_Answer"] = eng_ans

                # Extract relevant source passage snippet
                passages = rec.get("passages", {})
                trans_passages = passages.get("Translated_passages", [])
                eng_passages = passages.get("English_passages", [])
                is_sel = passages.get("is_selected", [])

                sel_snippet = ""
                for idx, sel in enumerate(is_sel):
                    if sel == 1:
                        if trans_passages and idx < len(trans_passages):
                            sel_snippet = trans_passages[idx]
                        elif eng_passages and idx < len(eng_passages):
                            sel_snippet = eng_passages[idx]
                        break

                if not sel_snippet:
                    if trans_passages and len(trans_passages) > 0:
                        sel_snippet = trans_passages[0]
                    elif eng_passages and len(eng_passages) > 0:
                        sel_snippet = eng_passages[0]

                rec["selected_snippet"] = sel_snippet
                records_by_lang[lang_name].append(rec)

            except Exception as e:
                pass

    return records_by_lang, all_found_langs


def generate_balanced_test_suite():
    """Generates ~20 balanced test questions covering English, Hindi, Marathi, Bengali, and other languages."""
    indexed_qids = load_indexed_query_ids()
    records_by_lang, all_found_langs = load_dataset_records(indexed_qids)

    test_items = []

    # 1. English Questions (3 to 5 questions extracted from dataset Eng_Query)
    eng_candidates = []
    for lang, recs in records_by_lang.items():
        for r in recs:
            if r.get("Eng_Query") and r.get("Eng_Answer") and len(r["Eng_Query"]) > 10:
                eng_candidates.append(r)

    # Deduplicate English queries
    seen_eng_queries = set()
    selected_eng = []
    for r in eng_candidates:
        eq = r["Eng_Query"].strip().lower()
        if eq not in seen_eng_queries:
            seen_eng_queries.add(eq)
            selected_eng.append(r)
        if len(selected_eng) >= 4:
            break

    for idx, r in enumerate(selected_eng):
        test_items.append({
            "lang_display": "English",
            "lang_code": "en",
            "query": r["Eng_Query"],
            "answer": r["Eng_Answer"],
            "query_id": r["query_id"],
            "snippet": r.get("selected_snippet", ""),
            "original_lang": r.get("language_name", "English")
        })

    # Priority Indic Languages
    target_prio_counts = [
        ("Hindi", 3),
        ("Marathi", 3),
        ("Bengali", 3)
    ]

    for lang_name, count in target_prio_counts:
        recs = records_by_lang.get(lang_name, [])
        added = 0
        for r in recs:
            if r.get("query") and r.get("Answer"):
                test_items.append({
                    "lang_display": lang_name,
                    "lang_code": r.get("target_lang", lang_name[:2].lower()),
                    "query": r["query"],
                    "answer": r["Answer"],
                    "query_id": r["query_id"],
                    "snippet": r.get("selected_snippet", ""),
                    "original_lang": lang_name
                })
                added += 1
                if added >= count:
                    break

    # Remaining languages (1 each to reach ~20 total questions)
    other_langs = [
        "Tamil", "Telugu", "Gujarati", "Kannada", "Malayalam",
        "Odia", "Punjabi", "Urdu", "Assamese", "Nepali"
    ]

    for lang_name in other_langs:
        recs = records_by_lang.get(lang_name, [])
        for r in recs:
            if r.get("query") and r.get("Answer"):
                test_items.append({
                    "lang_display": lang_name,
                    "lang_code": r.get("target_lang", lang_name[:2].lower()),
                    "query": r["query"],
                    "answer": r["Answer"],
                    "query_id": r["query_id"],
                    "snippet": r.get("selected_snippet", ""),
                    "original_lang": lang_name
                })
                break  # Pick 1 per language

    return test_items, all_found_langs


def print_report():
    test_items, all_found_langs = generate_balanced_test_suite()

    print("=" * 80)
    print("RAGE HH GOA — DATASET-BASED RAG TEST QUESTION GENERATOR")
    print("=" * 80)
    print(f"Total Languages Found in Dataset : {len(all_found_langs)}")
    print(f"Languages Available              : {', '.join(sorted(all_found_langs))}")
    print(f"Total Questions Selected          : {len(test_items)}")
    print("=" * 80)
    print()

    # SECTION 1: MAIN COPY-PASTE NUMBERED LIST FOR FRONTEND TESTING
    print("=" * 80)
    print("SECTION 1: MANUALLY COPY-PASTE FRONTEND TEST QUESTIONS")
    print("=" * 80)
    print("Copy each question below and paste it directly into the RAGE HH GOA frontend.")
    print("-" * 80)

    for idx, item in enumerate(test_items, 1):
        num_str = f"{idx:02d}"
        print(f"\nTEST {num_str} — {item['lang_display']}")
        print(f"Question: {item['query']}")

    print("\n" + "=" * 80)

    # SECTION 2: EXPECTED RESULTS & METADATA FOR AUDIT
    print("SECTION 2: EXPECTED RESULTS (Ground-Truth Dataset Verification)")
    print("=" * 80)
    print("Compare the backend RAG response against these dataset ground-truth values.")
    print("-" * 80)

    for idx, item in enumerate(test_items, 1):
        num_str = f"{idx:02d}"
        print(f"\n[TEST {num_str}]")
        print(f"ID                     : TEST_{num_str}_{item['lang_code'].upper()}")
        print(f"Language               : {item['lang_display']}")
        print(f"Original Dataset Query : {item['query']}")
        print(f"Expected Answer        : {item['answer']}")
        print(f"Query ID               : {item['query_id']}")
        print(f"Expected Language      : {item['lang_code']}")
        print(f"Source/Passage Snippet : {item['snippet'][:160]}...")

    print("\n" + "=" * 80)

    # SECTION 3: RECOMMENDED TESTING ORDER
    print("SECTION 3: RECOMMENDED TESTING ORDER")
    print("=" * 80)
    print("1. English exact dataset queries (TEST 01 to TEST 04)")
    print("2. Hindi exact dataset queries (TEST 05 to TEST 07)")
    print("3. Marathi exact dataset queries (TEST 08 to TEST 10)")
    print("4. Bengali exact dataset queries (TEST 11 to TEST 13)")
    print("5. Other available Indian languages (TEST 14 to TEST 23: Tamil, Telugu, Gujarati, Kannada, Malayalam, Odia, Punjabi, Urdu, Assamese, Nepali)")
    print("6. Multilingual & Edge cases (Voice input & manual language dropdown overrides)")
    print("=" * 80)


if __name__ == "__main__":
    print_report()
