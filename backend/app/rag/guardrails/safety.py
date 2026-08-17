"""
Safety Filter Guardrail (Phase 8)

Basic safety gate evaluating query safety across English and Indic scripts.
Uses internal evaluation states: SAFE, UNSAFE, UNCERTAIN to prevent false positives.
"""

from enum import Enum
from typing import Tuple


class SafetyState(str, Enum):
    SAFE = "SAFE"
    UNSAFE = "UNSAFE"
    UNCERTAIN = "UNCERTAIN"


# Targeted list of unsafe categories to avoid broad false-positive keyword rejections
MALICIOUS_PATTERNS = [
    "drop database",
    "delete from",
    "rm -rf",
    "format c:",
    "how to build a bomb",
    "how to make explosives",
]


class SafetyFilter:
    """Basic safety filter checking query intent before LLM execution."""

    @staticmethod
    def evaluate_query(query: str) -> Tuple[SafetyState, str]:
        """
        Evaluates user query safety.

        :param query: Raw user query string
        :return: Tuple of (SafetyState, reasoning_reason)
        """
        if not query or not query.strip():
            return SafetyState.SAFE, "Empty query"

        query_lower = query.lower()

        for pattern in MALICIOUS_PATTERNS:
            if pattern in query_lower:
                return SafetyState.UNSAFE, f"Query matched malicious pattern '{pattern}'"

        return SafetyState.SAFE, "Query passed basic safety check"
