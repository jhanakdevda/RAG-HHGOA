"""
Authoritative Web Search & Evidence Retrieval Service (Phase 3 & 4)

Provides fallback evidence retrieval for out-of-corpus user queries
using authoritative encyclopedic (Wikipedia REST API) and web APIs.
Outputs standard TextChunk objects with verified title, URL, domain, and snippet metadata.
"""

import logging
import urllib.request
import urllib.parse
import json
import re
from typing import List
from app.models.chunk import TextChunk

logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for retrieving factual web evidence snippets when local FAISS RAG has insufficient evidence."""

    def __init__(self, timeout: float = 4.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RAGE_HH_GOA_Bot/1.0"
        }

    def search(self, query: str, max_results: int = 3) -> List[TextChunk]:
        """
        Executes web search for query and returns list of TextChunk objects with web provenance metadata.
        """
        web_chunks: List[TextChunk] = []

        # 1. Primary: Search Wikipedia REST API for encyclopedic facts
        try:
            # Clean question preamble words for accurate Wikipedia article matching
            clean_query = re.sub(r'^(what is|where is|who is|which is|tell me about|how to|क्या है|कौन सी है|कौनती आहे|কোনটি)\s+', '', query, flags=re.IGNORECASE).strip() or query
            wiki_search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_query)}&utf8=&format=json"
            req = urllib.request.Request(wiki_search_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                hits = data.get("query", {}).get("search", [])

                for idx, hit in enumerate(hits[:max_results]):
                    title = hit.get("title", "")
                    snippet_raw = hit.get("snippet", "")
                    clean_snippet = re.sub(r'<[^>]+>', '', snippet_raw)

                    # Fetch page summary for rich extract
                    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title.replace(' ', '_'))}"
                    extract_text = clean_snippet
                    try:
                        s_req = urllib.request.Request(summary_url, headers=self.headers)
                        with urllib.request.urlopen(s_req, timeout=2.5) as s_resp:
                            s_data = json.loads(s_resp.read().decode("utf-8"))
                            if s_data.get("extract"):
                                extract_text = s_data.get("extract")
                    except Exception as s_err:
                        logger.debug(f"Wikipedia summary lookup failed for '{title}': {s_err}")

                    page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                    chunk_id = f"web_wiki_{idx}_{hit.get('pageid', idx)}"
                    full_txt = f"{title}: {extract_text}"

                    chunk = TextChunk(
                        chunk_id=chunk_id,
                        passage_index=0,
                        chunk_index=idx,
                        text=full_txt,
                        query_id=0,
                        is_selected=1,
                        language_code="en",
                        language_name="English (Web)",
                        source_lang="en",
                        target_lang="en",
                        char_count=len(full_txt),
                        word_count=len(full_txt.split()),
                        title=title,
                        url=page_url,
                        domain="en.wikipedia.org",
                        source_type="web"
                    )
                    web_chunks.append(chunk)

        except Exception as e:
            logger.warning(f"Wikipedia web search failed for '{query}': {e}")

        # 2. Secondary Fallback: DuckDuckGo Instant Answer API
        if not web_chunks:
            try:
                ddg_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&no_redirect=1"
                req = urllib.request.Request(ddg_url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    abstract = data.get("AbstractText", "")
                    heading = data.get("Heading", query)
                    abstract_url = data.get("AbstractURL", "https://duckduckgo.com")
                    domain = urllib.parse.urlparse(abstract_url).netloc or "duckduckgo.com"

                    if abstract:
                        full_txt = f"{heading}: {abstract}"
                        chunk = TextChunk(
                            chunk_id="web_ddg_0",
                            passage_index=0,
                            chunk_index=0,
                            text=full_txt,
                            query_id=0,
                            is_selected=1,
                            language_code="en",
                            language_name="English (Web)",
                            source_lang="en",
                            target_lang="en",
                            char_count=len(full_txt),
                            word_count=len(full_txt.split()),
                            title=heading,
                            url=abstract_url,
                            domain=domain,
                            source_type="web"
                        )
                        web_chunks.append(chunk)

            except Exception as e:
                logger.warning(f"DuckDuckGo search failed for '{query}': {e}")

        return web_chunks
