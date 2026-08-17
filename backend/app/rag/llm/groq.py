"""
Groq LLM Provider Adapter (Phase 7 / Phase 10 Low-Latency Provider)
"""

import os
import httpx
from typing import Optional, Iterator
from app.rag.llm.base import BaseLLMProvider
from app.core.config import get_settings


_shared_httpx_client: Optional[httpx.Client] = None


def get_shared_httpx_client(timeout: float = 3.0) -> httpx.Client:
    """Returns a module-level persistent httpx.Client with connection pooling and keep-alive enabled."""
    global _shared_httpx_client
    if _shared_httpx_client is None or _shared_httpx_client.is_closed:
        _shared_httpx_client = httpx.Client(
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20, keepalive_expiry=120.0),
            timeout=httpx.Timeout(timeout, connect=2.0)
        )
    return _shared_httpx_client


class GroqLLMProvider(BaseLLMProvider):
    """Groq API Provider Adapter utilizing persistent OpenAI-compatible client session with connection pooling and zero retry delays."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 3.0
    ):
        settings = get_settings()
        self.api_key = (
            api_key
            or settings.groq_api_key
            or os.getenv("GROQ_API_KEY")
            or settings.llm_api_key
            or os.getenv("LLM_API_KEY")
        )
        self.model_name = model_name or settings.llm_model or "groq/compound-mini"
        self.base_url = base_url or settings.llm_base_url or "https://api.groq.com/openai/v1"
        self.timeout = timeout
        self._client = None

        if not self.api_key:
            raise ValueError("Groq API key ('LLM_API_KEY' or 'GROQ_API_KEY') is required for 'groq' provider.")

        try:
            import openai
            http_cl = get_shared_httpx_client(self.timeout)
            self._client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=0,
                http_client=http_cl
            )
        except Exception:
            self._client = None

    def _get_client(self):
        """Returns initialized client or raises RuntimeError if openai package is missing."""
        if self._client is not None:
            return self._client
        try:
            import openai
            http_cl = get_shared_httpx_client(self.timeout)
            self._client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=0,
                http_client=http_cl
            )
            return self._client
        except ImportError as e:
            raise RuntimeError("Package 'openai' is required for Groq. Install with `pip install openai`.") from e

    def warm_connection(self):
        """Pre-warms DNS lookup, TCP socket connection, and TLS handshake to Groq API endpoint without consuming token quota."""
        try:
            http_cl = get_shared_httpx_client(self.timeout)
            http_cl.get(f"{self.base_url}/models", headers={"Authorization": f"Bearer {self.api_key}"})
            print(f"[GROQ WARMUP] TLS connection pre-warmed to {self.base_url}")
        except Exception as e:
            print(f"[GROQ WARMUP NOTE] Connection pre-warming skipped: {e}")

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Invokes Groq API using persistent OpenAI-compatible client session."""
        ans, _, _ = self.generate_with_usage(prompt, system_instruction)
        return ans

    def generate_with_usage(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: int = 16,
        temperature: float = 0.0,
        stop: Optional[list[str]] = None
    ) -> tuple[str, int, int]:
        """
        Invokes Groq API and returns tuple of (answer_text, prompt_tokens, completion_tokens).
        """
        client = self._get_client()
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.0,
                    max_tokens=max_tokens
                )
            except Exception as model_err:
                if "does not exist" in str(model_err).lower() or "404" in str(model_err):
                    self.model_name = "groq/compound-mini"
                    response = client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=0.0,
                        max_tokens=max_tokens
                    )
                else:
                    raise model_err

            text = ""
            prompt_tokens = 0
            completion_tokens = 0

            if response and response.choices and response.choices[0].message.content:
                text = response.choices[0].message.content.strip()

            if hasattr(response, "usage") and response.usage:
                prompt_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
                completion_tokens = getattr(response.usage, "completion_tokens", 0) or 0

            if not prompt_tokens:
                prompt_tokens = int(len((system_instruction or "").split() + prompt.split()) * 1.3)
            if not completion_tokens:
                completion_tokens = len(text.split())

            return text, prompt_tokens, completion_tokens
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "rate_limit" in err_msg.lower() or "rate limit" in err_msg.lower():
                raise RuntimeError("AI service is temporarily rate-limited. Please try again shortly.") from e
            elif "timeout" in err_msg.lower():
                raise RuntimeError("AI service timed out. Please try again.") from e
            raise RuntimeError(f"Groq API call failed: {err_msg}") from e

    def generate_stream(self, prompt: str, system_instruction: Optional[str] = None) -> Iterator[str]:
        """Invokes Groq API with streaming response for Time-To-First-Token (TTFT) measurement."""
        client = self._get_client()
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            stream = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0,
                max_tokens=45,
                stream=True
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "rate_limit" in err_msg.lower():
                raise RuntimeError("AI service is temporarily rate-limited. Please try again shortly.") from e
            raise RuntimeError(f"Groq API streaming call failed: {err_msg}") from e
