"""
Abstract Base Class for LLM Provider Adapters (Phase 7)
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMProvider(ABC):
    """Abstract interface for LLM provider adapters."""

    @abstractmethod
    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Generates text completion for a given prompt and optional system instruction.

        :param prompt: User prompt text including context blocks
        :param system_instruction: System prompt with grounding instructions
        :return: Generated answer string
        """
        pass
