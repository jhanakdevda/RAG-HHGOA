"""
Mock LLM Provider Adapter (Phase 7)

Zero-cost, offline deterministic provider for development, testing, and CI/CD pipelines.
Generates grounded responses directly from context blocks without external API calls.
"""

from typing import Optional
from app.rag.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider adapter requiring no API keys or internet connection."""

    def __init__(self, model_name: str = "mock-v1"):
        self.model_name = model_name

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Extracts relevant information from context blocks in the prompt or returns grounded summary.
        """
        if "CONTEXT BLOCKS:" in prompt:
            context_part = prompt.split("CONTEXT BLOCKS:")[1]
            if "USER QUESTION:" in context_part:
                context_part = context_part.split("USER QUESTION:")[0]

            lines = [line.strip() for line in context_part.splitlines() if line.strip() and not line.startswith("---")]
            if lines:
                # Return first substantive context line as grounded mock answer
                first_substantive = next((l for l in lines if len(l) > 10), lines[0])
                return f"संदर्भ के अनुसार: {first_substantive}"

        return "प्रदान किए गए संदर्भ में इस प्रश्न का उत्तर देने के लिए पर्याप्त जानकारी उपलब्ध नहीं है।"
