"""
Verification test for POST /ask endpoint with query 'How fast do eagles fly?'
"""

import sys
import json
import urllib.request
import urllib.error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_eagle_query():
    url = "http://127.0.0.1:8000/ask"
    payload = {
        "query": "How fast do eagles fly?",
        "top_k": 3,
        "preferred_answer_language": "en"
    }
    data_bytes = json.dumps(payload).encode("utf-8")

    print("=" * 80)
    print("SENDING REAL POST /ask FOR: 'How fast do eagles fly?'")
    print("=" * 80)

    try:
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except urllib.error.URLError as e:
        print(f"URL Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_eagle_query()
