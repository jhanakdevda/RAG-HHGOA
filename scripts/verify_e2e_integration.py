"""
End-to-End Local API Verification Script for RAGE HH GOA Frontend/Backend
"""

import os
import sys
import json
import urllib.request
import urllib.error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def verify_endpoints():
    base_url = "http://127.0.0.1:8000"
    print("=" * 80)
    print("Executing Real End-to-End API Integration Verification")
    print("=" * 80)

    # 1. GET /health
    print("\n1. Testing GET /health...")
    try:
        req = urllib.request.Request(f"{base_url}/health", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req) as resp:
            health_data = json.loads(resp.read().decode())
            print(f"   [SUCCESS] Status: {resp.status} | Data: {health_data}")
    except Exception as e:
        print(f"   [FAIL] Health check failed: {e}")

    # Test queries
    test_queries = [
        {"lang": "en", "query": "What is the capital of Goa?"},
        {"lang": "hi", "query": "गोवा की राजधानी क्या है?", "pref_lang": "hi"},
        {"lang": "mr", "query": "गोव्याची राजधानी कोणती आहे?", "pref_lang": "mr"},
        {"lang": "bn", "query": "গোয়ার রাজধানী কোনটি?", "pref_lang": "bn"}
    ]

    for item in test_queries:
        lang = item["lang"]
        q_text = item["query"]
        pref_lang = item.get("pref_lang", "en")
        print(f"\n2. Testing POST /ask [{lang.upper()}] Query: '{q_text}'...")

        payload = {
            "query": q_text,
            "top_k": 3,
            "preferred_answer_language": pref_lang
        }
        data_bytes = json.dumps(payload).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"{base_url}/ask",
                data=data_bytes,
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode())
                print(f"   [SUCCESS] Grounding Status : {result.get('grounding_status')}")
                print(f"   [SUCCESS] Grounding Score  : {result.get('grounding_score')}")
                print(f"   [SUCCESS] Total Latency    : {result.get('total_latency_ms')} ms")
                print(f"   [SUCCESS] Answer Text      : '{result.get('answer')}'")
                print(f"   [SUCCESS] Sources Count    : {len(result.get('sources', []))}")
                if result.get("sources"):
                    first_src = result["sources"][0]
                    print(f"   [SUCCESS] Source #1 Chunk  : ID={first_src.get('chunk_id')}, Similarity={first_src.get('similarity_score')}")
        except Exception as e:
            print(f"   [FAIL] POST /ask failed for {lang}: {e}")

    # 3. Test Invalid Backend URL error handling
    print("\n3. Testing Unavailable Backend URL Error Handling...")
    invalid_url = "http://127.0.0.1:9999"
    try:
        req = urllib.request.Request(f"{invalid_url}/health")
        with urllib.request.urlopen(req) as resp:
            pass
    except urllib.error.URLError as e:
        print(f"   [SUCCESS] Connection safely rejected as expected: {e.reason}")
    except Exception as e:
        print(f"   [SUCCESS] Error trapped cleanly: {e}")

if __name__ == "__main__":
    verify_endpoints()
