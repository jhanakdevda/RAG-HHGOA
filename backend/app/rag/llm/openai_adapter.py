"""
OpenAI LLM Provider Adapter (Phase 7 / Failover Provider)
"""

import os
from typing import Optional
from app.rag.llm.base import BaseLLMProvider
from app.core.config import get_settings


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI API Provider Adapter utilizing persistent client session and zero retry delays."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = "gpt-4o-mini",
        base_url: Optional[str] = None,
        timeout: float = 15.0
    ):
        settings = get_settings()
        self.api_key = (
            api_key
            or settings.openai_api_key
            or os.getenv("OPENAI_API_KEY")
            or settings.llm_api_key
            or os.getenv("LLM_API_KEY")
        )
        self.model_name = model_name or "gpt-4o-mini"
        self.base_url = base_url
        self.timeout = timeout
        self._client = None

        if self.api_key:
            try:
                import openai
                kwargs = {
                    "api_key": self.api_key,
                    "timeout": self.timeout,
                    "max_retries": 0
                }
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._client = openai.OpenAI(**kwargs)
            except Exception:
                self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise ValueError("OpenAI API key is required for OpenAI provider.")
        try:
            import openai
            kwargs = {
                "api_key": self.api_key,
                "timeout": self.timeout,
                "max_retries": 0
            }
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = openai.OpenAI(**kwargs)
            return self._client
        except ImportError as e:
            raise RuntimeError("Package 'openai' is not installed.") from e

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        client = self._get_client()
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0,
                max_tokens=75
            )
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            return ""
        except Exception as e:
            err_str = str(e).lower()
            import openai
            if isinstance(e, openai.AuthenticationError):
                raise RuntimeError("OpenAI authentication failed: Invalid API key.") from e
            elif isinstance(e, openai.RateLimitError) or "429" in err_str or "rate_limit" in err_str or "quota" in err_str:
                if "insufficient_quota" in err_str or "quota" in err_str:
                    raise RuntimeError("OpenAI account quota is exhausted. Please check billing details.") from e
                else:
                    raise RuntimeError("AI service is temporarily rate-limited. Please try again shortly.") from e
            elif isinstance(e, openai.NotFoundError) or "404" in err_str:
                raise RuntimeError(f"OpenAI model '{self.model_name}' not found or inaccessible.") from e
            elif isinstance(e, openai.APITimeoutError) or "timeout" in err_str:
                raise RuntimeError("AI service timed out. Please try again.") from e
            raise RuntimeError(f"OpenAI API call failed: {e}") from e
