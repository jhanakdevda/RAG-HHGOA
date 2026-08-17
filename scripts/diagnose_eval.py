import json
import os

sample_path = "data/sample/msmarco_xi_multilingual_sample.jsonl"
meta_path = "vector_store/chunk_metadata.jsonl"

with open(sample_path, "r", encoding="utf-8") as f:
    examples = [json.loads(line) for line in f if line.strip()]

with open(meta_path, "r", encoding="utf-8") as f:
    chunks = [json.loads(line) for line in f if line.strip()]

print(f"Total sample examples: {len(examples)}")
print(f"Total vector store chunks: {len(chunks)}")

# Map of (query_id, passage_index) present in vector store
index_passage_map = set()
for c in chunks:
    index_passage_map.add((c["query_id"], c["passage_index"]))

print(f"Unique (query_id, passage_index) in vector store: {len(index_passage_map)}")

# Check ground-truth selected passages per example
examples_with_selected = 0
examples_with_selected_in_index = 0

query_ground_truth_status = []

for ex in examples:
    q_id = ex["query_id"]
    target_lang = ex.get("target_lang", "en")
    is_sel_list = ex.get("passages", {}).get("is_selected", [])
    selected_indices = [idx for idx, sel in enumerate(is_sel_list) if sel == 1]
    
    if selected_indices:
        examples_with_selected += 1
    
    # Check if any selected passage is present in vector store
    in_index = any((q_id, p_idx) in index_passage_map for p_idx in selected_indices)
    if in_index:
        examples_with_selected_in_index += 1

    query_ground_truth_status.append({
        "query_id": q_id,
        "target_lang": target_lang,
        "selected_indices": selected_indices,
        "in_index": in_index
    })

print(f"Examples with at least one selected passage (is_selected == 1): {examples_with_selected} / {len(examples)}")
print(f"Examples whose selected passage is present in FAISS index: {examples_with_selected_in_index} / {len(examples)}")
