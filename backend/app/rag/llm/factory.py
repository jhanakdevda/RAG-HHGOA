"""
LLM Provider Factory (Phase 7 / Groq Production Provider)

Dynamically instantiates and manages singleton instances of the LLM provider adapter.
"""

from typing import Optional
from app.core.config import get_settings
from app.rag.llm.base import BaseLLMProvider
from app.rag.llm.mock import MockLLMProvider
from app.rag.llm.groq import GroqLLMProvider


_cached_provider = None
_cached_key_tuple = None


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None
) -> BaseLLMProvider:
    """
    Returns a singleton instance of BaseLLMProvider based on configuration settings (default: Groq).
    """
    global _cached_provider, _cached_key_tuple
    settings = get_settings()

    provider = (provider_name or settings.llm_provider or "groq").strip().lower()
    model = model_name or settings.llm_model or "llama-3.1-8b-instant"
    key = api_key or settings.groq_api_key or settings.effective_llm_api_key
    url = base_url or settings.llm_base_url or "https://api.groq.com/openai/v1"
    t_out = timeout if timeout is not None else settings.llm_timeout

    key_tuple = (provider, model, key, url, t_out)
    if _cached_provider is not None and _cached_key_tuple == key_tuple:
        return _cached_provider

    if provider == "mock":
        inst = MockLLMProvider(model_name=model)
    elif provider == "gemini":
        try:
            from app.rag.llm.gemini import GeminiLLMProvider
            inst = GeminiLLMProvider(api_key=key, model_name=model, timeout=t_out)
        except Exception:
            inst = GroqLLMProvider(api_key=key, model_name=model, base_url=url, timeout=t_out)
    elif provider == "openai":
        from app.rag.llm.openai_adapter import OpenAILLMProvider
        inst = OpenAILLMProvider(api_key=key, model_name=model, base_url=url, timeout=t_out)
    elif provider == "ollama":
        from app.rag.llm.ollama import OllamaLLMProvider
        inst = OllamaLLMProvider(model_name=model, base_url=url, timeout=t_out)
    elif provider == "groq":
        inst = GroqLLMProvider(api_key=key, model_name=model, base_url=url, timeout=t_out)
    else:
        inst = GroqLLMProvider(api_key=key, model_name=model, base_url=url, timeout=t_out)

    _cached_provider = inst
    _cached_key_tuple = key_tuple
    return inst
