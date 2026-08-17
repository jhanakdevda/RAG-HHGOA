"""
Ollama Local LLM Provider Adapter (Phase 7)
"""

from typing import Optional
import urllib.request
import json
from app.rag.llm.base import BaseLLMProvider


class OllamaLLMProvider(BaseLLMProvider):
    """Ollama Local LLM Provider Adapter."""

    def __init__(
        self,
        model_name: str = "llama3:latest",
        base_url: Optional[str] = "http://localhost:11434",
        timeout: float = 15.0
    ):
        self.model_name = model_name
        self.base_url = (base_url or "http://localhost:11434").rstrip("/")
        self.timeout = timeout

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Invokes local Ollama /api/generate REST endpoint via stdlib urllib."""
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_instruction or "",
            "stream": False,
            "options": {"temperature": 0.1}
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            http_req = urllib.request.Request(
                endpoint,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(http_req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"Ollama API call failed at '{endpoint}': {e}") from e
