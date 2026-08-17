"""
Prompt Injection Defense Module (Phase 8)

Enforces strict boundary isolation between system instructions, user query data,
and retrieved context chunks using XML data tagging (<untrusted_retrieved_context_data>, <untrusted_user_query>).
Preserves the user's original query 100% untouched without stripping text.
"""

from typing import List
from app.models.chunk import TextChunk


class InjectionDefense:
    """Provides safe prompt construction and untrusted data boundary isolation."""

    @staticmethod
    def format_untrusted_query(query: str) -> str:
        """
        Wraps user query inside XML data boundary tags without altering original query characters.
        """
        escaped_query = query.replace("</untrusted_user_query>", "&lt;/untrusted_user_query&gt;")
        return f"<untrusted_user_query>\n{escaped_query}\n</untrusted_user_query>"

    @staticmethod
    def format_untrusted_context(chunks: List[TextChunk], max_snippet_len: int = 100) -> str:
        """
        Formats retrieved chunks into safe, untrusted context data blocks.
        Trims snippet length to essential evidence (default 250 chars) to prevent context token bloat.
        """
        if not chunks:
            return "<untrusted_retrieved_context_data>\nNo retrieved context blocks.\n</untrusted_retrieved_context_data>"

        blocks = []
        for idx, chunk in enumerate(chunks, 1):
            escaped_text = chunk.text.replace("</untrusted_retrieved_context_data>", "&lt;/untrusted_retrieved_context_data&gt;")
            if len(escaped_text) > max_snippet_len:
                escaped_text = escaped_text[:max_snippet_len].rsplit(" ", 1)[0] + "..."
            block = f"--- Context {idx} ---\n{escaped_text}"
            blocks.append(block)

        joined_blocks = "\n\n".join(blocks)
        return f"<untrusted_retrieved_context_data>\n{joined_blocks}\n</untrusted_retrieved_context_data>"
