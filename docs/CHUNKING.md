# Adaptive Semantic Chunking Documentation

**Module**: `backend/app/rag/chunker.py`  
**Model**: `backend/app/models/chunk.py` (`TextChunk`)  
**Processed Dataset**: `data/processed/msmarco_xi_hi_chunks.jsonl`  
**Target Language**: Hindi (`hi`) / Devanagari Script

---

## 1. Chunking Architecture & Strategy

In RAG pipelines, naive fixed-character splitting (e.g. slicing every 250 characters regardless of word or sentence boundaries) damages semantic coherence and truncates key information. 

**Adaptive Semantic Chunking** solves this by:
1. **Splitting on Semantic Sentence Boundaries**: Using Devanagari-aware regex matching for Purna Viram (`।`, `॥`), question mark (`?`), exclamation (`!`), period (`.`), and line breaks.
2. **Preserving Sentence Integrity**: Never splitting sentences or Devanagari words mid-character.
3. **Adaptive Merging**: Grouping consecutive sentences until reaching target character boundaries (~300–500 characters / ~50–90 words).
4. **Context Overlap**: Overlapping trailing sentences (`overlap_sentences=1`) between adjacent chunks to maintain context across chunk boundaries.
5. **Complete Provenance Preservation**: Retaining query IDs, passage indices, character offsets, and ground truth relevance selection flags (`is_selected`).

---

## 2. Devanagari Sentence Boundary Rules

Sentence splitting is governed by `AdaptiveSemanticChunker.SENTENCE_END_PATTERN`:

```python
SENTENCE_END_PATTERN = re.compile(r'(?<=[।॥?!.\n])\s+')
```

| Delimiter | Name / Symbol | Example |
|-----------|---------------|---------|
| `।` | Purna Viram (Devanagari full stop) | `पणजी गोवा की राजधानी है।` |
| `॥` | Deergh Viram (Double Purna Viram) | `जय हिन्द॥` |
| `?` | Question Mark | `गोवा की राजधानी क्या है?` |
| `!` | Exclamation Mark | `कितना सुंदर दृश्य है!` |
| `.` | Latin Period (for mixed Hindi/English text) | `Panaji is the capital.` |
| `\n` | Line breaks / Paragraph breaks | Paragraph demarcation |

---

## 3. Provenance & Chunk Metadata Schema (`TextChunk`)

Each output chunk is represented by the `TextChunk` Pydantic model:

```json
{
  "chunk_id": "100001_p0_c0",
  "text": "पणजी भारतीय राज्य गोवा की राजधानी और उत्तरी गोवा जिले का मुख्यालय है। यह तिसवाड़ी तालुका में मांडवी नदी के मुहाने के तट पर स्थित है।",
  "query_id": 100001,
  "passage_index": 0,
  "chunk_index": 0,
  "is_selected": 1,
  "char_count": 133,
  "word_count": 25,
  "start_char": 0,
  "end_char": 133
}
```

### Schema Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `chunk_id` | `str` | Format: `{query_id}_p{passage_index}_c{chunk_index}` |
| `text` | `str` | Complete Devanagari chunk string |
| `query_id` | `int` | Parent MS MARCO query ID |
| `passage_index` | `int` | Zero-based index of original passage within query example |
| `chunk_index` | `int` | Zero-based sequence index of chunk within passage |
| `is_selected` | `int` | Inherited ground truth label (`1` = relevant passage, `0` = non-relevant) |
| `char_count` | `int` | Total character count of chunk text |
| `word_count` | `int` | Total word count of chunk text |
| `start_char` | `int` | Start character offset in original passage |
| `end_char` | `int` | End character offset in original passage |

---

## 4. Batch Processing Metrics (`data/processed/msmarco_xi_hi_chunks.jsonl`)

Running `python scripts/process_chunks.py` on the 100-example development sample yields:

- **Total Examples Processed**: 100
- **Total Passages Chunked**: 300
- **Total Text Chunks Generated**: 300
- **Relevant Chunks (`is_selected == 1`)**: 100
- **Average Chunk Character Length**: 121.4 chars
- **Average Chunk Word Count**: 21.8 words
- **Output File Size**: 147.15 KB

---

## 5. Next Steps for Phase 5 (FAISS Vector Store)

In Phase 5, these `TextChunk` records will be embedded using a sentence transformer model (e.g. `sentence-transformers/LaBSE` or `multilingual-e5-base`) and indexed into a FAISS vector database for fast similarity retrieval.
