"""
Google Gemini LLM Provider Adapter (Phase 7 / Modern API)
"""

import os
from typing import Optional
from app.rag.llm.base import BaseLLMProvider
from app.core.config import get_settings


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini API Provider Adapter supporting google.genai and google.generativeai SDKs."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, timeout: float = 15.0):
        settings = get_settings()
        self.api_key = api_key or settings.effective_llm_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")

        target_model = model_name or settings.llm_model
        if not target_model or target_model in ("mock-v1", "gemini-1.5-flash"):
            target_model = "gemini-flash-latest"

        self.model_name = target_model
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("Gemini API key ('LLM_API_KEY' or 'GEMINI_API_KEY') is required for 'gemini' provider.")

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Invokes Google Gemini API via google.genai SDK or legacy fallback."""
        # Method 1: Official google.genai SDK
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            config = types.GenerateContentConfig(
                temperature=0.1,
                system_instruction=system_instruction if system_instruction else None
            )
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            if response and response.text:
                return response.text.strip()
        except Exception:
            pass

        # Method 2: Legacy google.generativeai SDK
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}") from e
