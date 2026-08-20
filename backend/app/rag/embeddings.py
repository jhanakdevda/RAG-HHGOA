"""
Embedding Service (Phase 4 / Phase 11 Ultra-Low Latency Vector Encoding)

Handles multi-lingual dense vector embedding generation using FastEmbed (ONNX)
or SentenceTransformers as fallback.
"""

import os
from typing import List, Optional
import numpy as np
from app.core.config import get_settings


_shared_model = None
_shared_model_name = None
_model_type = None  # 'fastembed' or 'sentence_transformers'
DEFAULT_MODEL_NAME = "Xenova/distiluse-base-multilingual-cased-v2"


class EmbeddingService:
    """Service to load embedding model once and compute L2-normalized dense vector representations."""

    def __init__(self, model_name: Optional[str] = None):
        settings = get_settings()
        self.model_name = (
            model_name
            or getattr(settings, "embedding_model_name", None)
            or os.getenv("EMBEDDING_MODEL_NAME")
            or DEFAULT_MODEL_NAME
        )
        self.dimension = int(
            getattr(settings, "embedding_dimension", None)
            or os.getenv("EMBEDDING_DIMENSION", 768)
        )
        self._model = _shared_model

    def _load_model(self):
        """Pre-loads FastEmbed (ONNX) or SentenceTransformer model once into class-level singleton."""
        global _shared_model, _shared_model_name, _model_type
        if _shared_model is None or _shared_model_name != self.model_name:
            _shared_model = None
            _shared_model_name = self.model_name
            # Try lightweight FastEmbed ONNX Runtime first (no torch required, < 60MB RAM/disk)
            try:
                from fastembed import TextEmbedding
                from fastembed.common.model_description import PoolingType, ModelSource

                # Register Xenova INT8 Quantized DistilUSE ONNX model (768 dim, ~291 MB RAM)
                try:
                    TextEmbedding.add_custom_model(
                        model="Xenova/distiluse-base-multilingual-cased-v2",
                        pooling=PoolingType.MEAN,
                        normalization=True,
                        sources=ModelSource(hf="Xenova/distiluse-base-multilingual-cased-v2"),
                        dim=768,
                        model_file="onnx/model_quantized.onnx",
                        description="Xenova INT8 Quantized DistilUSE Multilingual ONNX model",
                        size_in_gb=0.14
                    )
                except ValueError:
                    pass  # Model already registered

                # Targeted single-file pre-download to prevent HF snapshot_download overhead
                try:
                    from huggingface_hub import hf_hub_download
                    _hf_repo = "Xenova/distiluse-base-multilingual-cased-v2"
                    for _fn in ["onnx/model_quantized.onnx", "tokenizer.json", "config.json", "tokenizer_config.json", "special_tokens_map.json"]:
                        hf_hub_download(repo_id=_hf_repo, filename=_fn)
                except Exception as _dl_err:
                    print(f"[EMBEDDINGS NOTE] Targeted pre-download notice: {_dl_err}")

                _shared_model = TextEmbedding(
                    model_name=self.model_name,
                    threads=1,
                    enable_cpu_mem_arena=False
                )
                _model_type = "fastembed"
                list(_shared_model.embed(["warmup"]))
                print(f"[EMBEDDINGS] Loaded lightweight FastEmbed ONNX model: {self.model_name}")
            except Exception as fe_err:
                print(f"[EMBEDDINGS NOTE] FastEmbed load skipped ({fe_err}), falling back to sentence_transformers...")
                try:
                    import torch
                    from sentence_transformers import SentenceTransformer
                    torch.set_num_threads(4)
                    _shared_model = SentenceTransformer(self.model_name)
                    _model_type = "sentence_transformers"
                    _shared_model.encode(sentences=["warmup"], convert_to_numpy=True, normalize_embeddings=True)
                    print(f"[EMBEDDINGS] Loaded SentenceTransformers PyTorch model: {self.model_name}")
                except Exception as st_err:
                    raise RuntimeError(f"Failed to load any embedding model: {st_err}") from st_err

            self._model = _shared_model
        else:
            self._model = _shared_model

    def encode_texts(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True
    ) -> np.ndarray:
        """Generates dense vector embeddings for a list of text strings."""
        if not texts:
            dim = self.dimension
            return np.empty((0, dim), dtype=np.float32)

        self._load_model()

        if _model_type == "fastembed":
            generators = self._model.embed(texts, batch_size=batch_size)
            raw = np.array(list(generators), dtype=np.float32)
            if normalize and raw.shape[0] > 0:
                norms = np.linalg.norm(raw, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                raw = raw / norms
            return raw.astype(np.float32)
        else:
            import torch
            with torch.inference_mode():
                embeddings = self._model.encode(
                    sentences=texts,
                    batch_size=batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=normalize
                )
            return embeddings.astype(np.float32)

    def encode_query(self, query: str, normalize: bool = True) -> np.ndarray:
        """Helper to encode a single query string into a 2D embedding array."""
        return self.encode_texts([query], batch_size=1, normalize=normalize)

