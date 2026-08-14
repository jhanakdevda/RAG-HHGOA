# MS MARCO-XI Dataset Documentation

**Dataset**: [AI4Bharat MS MARCO-XI](https://huggingface.co/datasets/ai4bharat/MSMARCO-XI)  
**Configuration**: Hindi (`hi` / `hin`)  
**Purpose**: Passage corpus for Retrieval-Augmented Generation (RAG), speech-to-text question answering, vector index evaluation, and grounded answer verification.

---

## 1. Overview

MS MARCO (Microsoft Machine Reading Comprehension) is a benchmark dataset for machine reading comprehension and passage retrieval. **AI4Bharat MS MARCO-XI** extends this benchmark by providing high-quality translations across 14 Indic languages, including Hindi (`hi`).

### Key Highlights
- **Repository**: `ai4bharat/MSMARCO-XI`
- **Primary Target Language**: Hindi (`target_lang: "hi"`)
- **Source Language**: English (`source_lang: "en"`)
- **Format**: Parquet format in HF repository (`train/hintrain.parquet`, `validation/hinval.parquet`)

---

## 2. Dataset Scale & Metrics

The scale metrics verified directly via the Hugging Face Datasets Server API (`/size` and `/info` endpoints):

| Metric | Total Dataset | Train Split | Validation Split |
|--------|---------------|-------------|------------------|
| **Total Rows** | 11,451,314 | 10,080,140 | 1,371,174 |
| **Parquet File Size (Compressed)** | 51.80 GB | 45.67 GB | 6.13 GB |
| **Uncompressed Memory Size** | 136.57 GB | 120.97 GB | 15.60 GB |
| **Hindi (`hin`) Parquet Size** | ~4.00 GB | 3.55 GB | 440 MB |
| **Hindi (`hin`) Row Count** | ~900,000 | ~800,000 | 97,941 |

---

## 3. Verified Schema & Structure

Each example record contains the following fields:

```json
{
  "source_lang": "en",
  "target_lang": "hi",
  "query_id": 100001,
  "query_type": "description",
  "query": "गोवा की राजधानी क्या है और यह क्यों प्रसिद्ध है?",
  "Answer": "पणजी (Panaji) गोवा की राजधानी है। यह अपने मांडवी नदी तट...",
  "Eng_Query": "What is the capital of Goa and why is it famous?",
  "Eng_Answer": "Panaji is the capital of Goa. It is famous for...",
  "meta": {
    "model_name": "IndicTrans2",
    "temperature": 0.0,
    "max_tokens": 512,
    "top_p": 1.0,
    "frequency_penalty": 0,
    "presence_penalty": 0
  },
  "passages": {
    "English_passages": [
      "Panaji is the capital of the Indian state of Goa...",
      "Goa is a state on the southwestern coast of India..."
    ],
    "Translated_passages": [
      "पणजी भारतीय राज्य गोवा की राजधानी है...",
      "गोवा भारत के दक्षिण-पश्चिम तट पर स्थित राज्य है..."
    ],
    "is_selected": [1, 0]
  }
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `query_id` | `int64` | Unique numerical query identification number |
| `query_type` | `string` | Query classification category (e.g., `description`, `numeric`, `location`, `entity`) |
| `source_lang` | `string` | Source language ISO code (`"en"`) |
| `target_lang` | `string` | Target language ISO code (`"hi"`) |
| `query` | `string` | Hindi translated query string |
| `Answer` | `string` | Hindi reference ground truth answer |
| `Eng_Query` | `string` | Original English query string |
| `Eng_Answer` | `string` | Original English ground truth answer |
| `meta` | `struct` | Translation model metadata (`model_name`, `temperature`, `max_tokens`, `top_p`, `frequency_penalty`, `presence_penalty`) |
| `passages` | `struct` | Container for English and Hindi translated passages, alongside binary ground truth relevance flags |
| `passages.English_passages` | `list[string]` | List of candidate passages in English |
| `passages.Translated_passages` | `list[string]` | List of candidate passages in Hindi |
| `passages.is_selected` | `list[int64]` | Binary list (`1` = passage contains answer, `0` = passage does not contain answer) |

---

## 4. Technical Findings & Inspection Notes

### Hugging Face Datasets Server API Findings
- The lightweight HF Datasets Server `/info`, `/size`, and `/splits` endpoints return complete metadata.
- The `/rows` endpoint returns HTTP 500 error (`TooBigRowGroupsError`). This occurs because the single row group in the remote Parquet files exceeds the Hugging Face server worker limit of 300MB.

### Development Sample Strategy
To ensure fast, reliable local development without downloading the multi-gigabyte full dataset:
- We created a local sample file at `data/sample/msmarco_xi_hi_sample.jsonl`.
- The sample contains **100 realistic examples** strictly adhering to the verified Pydantic schema (`backend/app/models/dataset.py`).
- All Phase 3 unit tests validate against this local JSONL file without network overhead.

---

## 5. RAG Pipeline Integration Plan

The verified dataset fields directly power the upcoming RAG pipeline phases:

1. **Phase 4 (Chunking)**: `passages.Translated_passages` will be processed using adaptive/semantic chunking.
2. **Phase 5 (Vector Store)**: Chunked passage embeddings will be indexed in a FAISS vector store.
3. **Phase 6 & 7 (Retrieval & Voice)**: Voice queries transcribed by Sarvam STT will retrieve top-K relevant passages from FAISS.
4. **Phase 8 & 9 (LLM & Guardrails)**: Retrieved passages will be fed into the LLM context to generate grounded answers in Hindi, evaluated against `Answer` and `passages.is_selected`.
