"""
Test Enhanced Web Retrieval Service using Wikipedia REST & DuckDuckGo APIs
"""

import sys
import json
import urllib.request
import urllib.parse
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def search_web_evidence(query: str, max_results: int = 3):
    """Retrieves authoritative web evidence for out-of-corpus queries."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RAGE_HH_GOA_Bot/1.0"
    }

    results = []

    # 1. Search Wikipedia REST API for search hits
    wiki_search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
    try:
        req = urllib.request.Request(wiki_search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            hits = data.get("query", {}).get("search", [])

            for hit in hits[:max_results]:
                title = hit.get("title", "")
                snippet_raw = hit.get("snippet", "")
                clean_snippet = re.sub(r'<[^>]+>', '', snippet_raw)

                # Fetch page summary for high-quality evidence
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title.replace(' ', '_'))}"
                extract_text = clean_snippet
                try:
                    s_req = urllib.request.Request(summary_url, headers=headers)
                    with urllib.request.urlopen(s_req, timeout=3) as s_resp:
                        s_data = json.loads(s_resp.read().decode("utf-8"))
                        if s_data.get("extract"):
                            extract_text = s_data.get("extract")
                except Exception:
                    pass

                page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                results.append({
                    "title": title,
                    "url": page_url,
                    "domain": "en.wikipedia.org",
                    "snippet": extract_text,
                    "score": 0.88
                })
    except Exception as e:
        print(f"Wikipedia search warning: {e}")

    # 2. DuckDuckGo Instant Answer API Fallback / Supplement
    if not results:
        ddg_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&no_redirect=1"
        try:
            req = urllib.request.Request(ddg_url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("AbstractText"):
                    results.append({
                        "title": data.get("Heading", query),
                        "url": data.get("AbstractURL", "https://duckduckgo.com"),
                        "domain": urllib.parse.urlparse(data.get("AbstractURL", "")).netloc or "duckduckgo.com",
                        "snippet": data.get("AbstractText"),
                        "score": 0.85
                    })
        except Exception as e:
            print(f"DuckDuckGo API error: {e}")

    return results

if __name__ == "__main__":
    res = search_web_evidence("What is the capital of Goa?")
    print(json.dumps(res, indent=2, ensure_ascii=False))
