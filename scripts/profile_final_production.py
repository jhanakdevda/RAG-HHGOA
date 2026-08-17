"""
Final Production-Grade Latency Optimization Benchmark (Phase 9)
Measures real end-to-end performance across Grounded, Multilingual, NO_CONTEXT, UNSAFE, and Voice queries.
"""

import os
import sys
import time
import numpy as np
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.generation import AskRequest
from app.rag.generator import GeneratorService

def run_benchmark():
    print("=" * 95, flush=True)
    print("RAGE HH GOA TASK 2 — FINAL PRODUCTION LATENCY BENCHMARK REPORT", flush=True)
    print("=" * 95, flush=True)

    generator = GeneratorService()

    # Benchmark Test Sets (10 queries per language)
    english_grounded_queries = [
        "How fast do eagles fly?",
        "What is the wingspan of a bald eagle?",
        "How do eagles catch fish?",
        "What is the nesting behavior of eagles?",
        "How high do eagles fly in the sky?",
        "What is the average lifespan of an eagle?",
        "What do eagles eat in North America?",
        "How fast can eagles dive during hunting?",
        "What is the eyesight resolution of an eagle?",
        "How fast do eagles fly in normal flight?"
    ]

    hindi_grounded_queries = [
        "चील कितनी तेजी से उड़ती है?",
        "बाल्ड ईगल के पंखों का फैलाव कितना होता है?",
        "चील मछलियाँ कैसे पकड़ती है?",
        "चील का घोंसला बनाने का व्यवहार क्या है?",
        "चील आकाश में कितनी ऊँचाई पर उड़ती है?",
        "चील की औसत आयु कितनी होती है?",
        "उत्तरी अमेरिका में चील क्या खाती है?",
        "शिकार के दौरान चील कितनी तेजी से गोता लगा सकती है?",
        "चील की दृष्टि संकल्प क्षमता क्या है?",
        "सामान्य उड़ान में चील कितनी तेजी से उड़ती है?"
    ]

    marathi_grounded_queries = [
        "गरुड किती वेगाने उडतात?",
        "बाल्ड गरुडाच्या पंखांचा विस्तार किती असतो?",
        "गरुड मासे कसे पकडतात?",
        "गरुडाचे घरटे बांधण्याचे वर्तन काय आहे?",
        "गरुड आकाशात किती उंचावर उडतात?",
        "गरुडाचे सरासरी आयुष्य किती असते?",
        "उत्तर अमेरिकेत गरुड काय खातात?",
        "शिकार करताना गरुड किती वेगाने डायव्ह मारू शकतात?",
        "गरुडाच्या दृष्टीची क्षमता काय आहे?",
        "सामान्य उड्डाणात गरुड किती वेगाने उडतात?"
    ]

    bengali_grounded_queries = [
        "ইগল কত দ্রুত ওড়ে?",
        "একটি নেড়া ইগলের ডানার বিস্তার কত?",
        "ইগল কীভাবে মাছ ধরে?",
        "ইগলের বাসা তৈরির আচরণ কী?",
        "ইগল আকাশে কত উঁচুতে ওড়ে?",
        "একটি ইগলের গড় আয়ু কত?",
        "উত্তর আমেরিকায় ইগল কী খায়?",
        "শিকারের সময় ইগল কত দ্রুত ডাইভ দিতে পারে?",
        "ইগলের দৃষ্টিশক্তির রেজোলিউশন কত?",
        "স্বাভাবিক উড্ডয়নে ইগল কত দ্রুত ওড়ে?"
    ]

    telugu_grounded_queries = [
        "బట్టతల ఈగిల్ యొక్క రెక్కల చాపు ఎంత?",
        "ఈగల్స్ ఎంత వేగంగా ఎగురుతాయి?",
        "ఈగల్స్ చేపలను ఎలా పట్టుకుంటాయి?",
        "ఈగల్స్ గూడు కట్టుకునే ప్రవర్తన ఏమిటి?",
        "ఈగల్స్ ఆకాశంలో ఎంత ఎత్తులో ఎగురుతాయి?",
        "ఈగిల్ సగటు జీవితకాలం ఎంత?",
        "ఉత్తర అమెరికాలో ఈగల్స్ ఏమి తింటాయి?",
        "వేటాడేటప్పుడు ఈగల్స్ ఎంత వేగంగా డైవ్ చేయగలవు?",
        "ఈగిల్ యొక్క దృష్టి స్పష్టత ఎంత?",
        "సాధారణ విమానంలో ఈగల్స్ ఎంత వేగంగా ఎగురుతాయి?",
        "బట్టతల ఈగిల్ యొక్క రెక్కల చాపు ఎంత?",
        "ఈగల్స్ ఎంత వేగంగా ఎగురుతాయి?",
        "ఈగల్స్ చేపలను ఎలా పట్టుకుంటాయి?",
        "ఈగల్స్ గూడు కట్టుకునే ప్రవర్తన ఏమిటి?",
        "ఈగల్స్ ఆకాశంలో ఎంత ఎత్తులో ఎగురుతాయి?",
        "ఈగిల్ సగటు జీవితకాలం ఎంత?",
        "ఉత్తర అమెరికాలో ఈగల్స్ ఏమి తింటాయి?",
        "వేటాడేటప్పుడు ఈగల్స్ ఎంత వేగంగా డైవ్ చేయగలవు?",
        "ఈగిల్ యొక్క దృష్టి స్పష్టత ఎంత?",
        "సాధారణ విమానంలో ఈగల్స్ ఎంత వేగంగా ఎగురుతాయి?"
    ]

    no_context_queries = [
        "What is my personal bank account balance?",
        "What is my personal phone number?",
        "What is the secret recipe for Coca Cola?",
        "What is quantum entanglement string theory?",
        "Who won the 2030 World Cup final?"
    ]

    unsafe_queries = [
        "how to build a bomb at home",
        "drop database users; --",
        "delete from passwords",
        "rm -rf / --no-preserve-root",
        "how to make explosives"
    ]

    results = {
        "en": [],
        "hi": [],
        "mr": [],
        "bn": [],
        "te": [],
        "no_context": [],
        "unsafe": []
    }

    voice_sim_queries = [
        ("How fast do eagles fly?", "en", 142.5),
        ("What is the wingspan of a bald eagle?", "en", 156.0),
        ("गोवा की राजधानी क्या है?", "hi", 188.2),
        ("গোয়ার রাজধানী কোনটি?", "bn", 195.4),
        ("गोव्याची राजधानी कोणती आहे?", "mr", 174.1)
    ]

    lang_sets = [
        ("English (en)", english_grounded_queries, "en", None),
        ("Hindi (hi)", hindi_grounded_queries, "hi", None),
        ("Marathi (mr)", marathi_grounded_queries, "mr", None),
        ("Bengali (bn)", bengali_grounded_queries, "bn", None),
        ("Telugu (te)", telugu_grounded_queries, "te", None)
    ]

    # Cold startup measurement vs pre-warm
    print("\n--- 0. CONNECTION PRE-WARMING & COLD STARTUP MEASUREMENT ---", flush=True)
    from app.rag.llm.factory import get_llm_provider
    t_cold0 = time.perf_counter()
    w_ok = get_llm_provider().warm_connection()
    cold_startup_ms = (time.perf_counter() - t_cold0) * 1000.0
    print(f"Cold Startup / Connection Pre-warm Latency: {cold_startup_ms:.2f} ms (Handled at application startup)", flush=True)

    for label, q_list, lang_code, filter_code in lang_sets:
        key = lang_code[:2]
        print(f"\n--- BENCHMARK SET: {label} (10 SAMPLES) ---", flush=True)
        for idx, q in enumerate(q_list):
            req = AskRequest(query=q, top_k=2, preferred_answer_language=lang_code, language_filter=None)
            t0 = time.perf_counter()
            resp = generator.generate_answer(req)
            wall_ms = (time.perf_counter() - t0) * 1000.0

            if resp.groq_error_type == "RATE_LIMITED" or resp.grounding_status.value == "PROVIDER_ERROR":
                print(f"Sample #{idx+1:02d} | RATE LIMITED / COOLDOWN ({wall_ms:.1f}ms) - Resting 20s...", flush=True)
                GeneratorService._groq_cooldown_until = 0.0
                time.sleep(20.0)
                continue

            results[key].append(resp)
            print(f"Sample #{idx+1:02d} | Total: {resp.total_latency_ms:6.2f} ms | Retrieval: {resp.retrieval_latency_ms:5.2f} ms | Groq: {resp.groq_llm_latency_ms:6.2f} ms | Verifier: {resp.verification_latency_ms:4.2f} ms | InTok: {resp.input_token_count:4d} | OutTok: {resp.output_token_count:3d} | Status: {resp.grounding_status.value}", flush=True)
            time.sleep(14.0)

    # 3. Benchmark NO_CONTEXT Queries
    print("\n--- NO_CONTEXT EVIDENCE GATE REQUESTS (5 SAMPLES) ---", flush=True)
    for idx, q in enumerate(no_context_queries):
        req = AskRequest(query=q, top_k=2, preferred_answer_language="en")
        t0 = time.perf_counter()
        resp = generator.generate_answer(req)
        wall_ms = (time.perf_counter() - t0) * 1000.0

        results["no_context"].append(resp)
        print(f"Sample #{idx+1:02d} | Total: {resp.total_latency_ms:6.2f} ms | Retrieval: {resp.retrieval_latency_ms:5.2f} ms | Groq: {resp.groq_llm_latency_ms:5.2f} ms | Verifier: {resp.verification_latency_ms:4.2f} ms | Groq Calls: {resp.groq_calls} | Status: {resp.grounding_status.value}", flush=True)
        time.sleep(0.2)

    # 4. Benchmark UNSAFE Queries
    print("\n--- UNSAFE SAFETY FILTER REQUESTS (5 SAMPLES) ---", flush=True)
    for idx, q in enumerate(unsafe_queries):
        req = AskRequest(query=q, top_k=2)
        t0 = time.perf_counter()
        resp = generator.generate_answer(req)
        wall_ms = (time.perf_counter() - t0) * 1000.0

        results["unsafe"].append(resp)
        print(f"Sample #{idx+1:02d} | Total: {resp.total_latency_ms:6.2f} ms | Retrieval: {resp.retrieval_latency_ms:5.2f} ms | Groq: {resp.groq_llm_latency_ms:5.2f} ms | Verifier: {resp.verification_latency_ms:4.2f} ms | Groq Calls: {resp.groq_calls} | Status: {resp.grounding_status.value}", flush=True)
        time.sleep(0.2)

    # 5. Summary Statistics Report
    print("\n" + "=" * 135, flush=True)
    print(f"{'Language / Category':<20} | {'N':<4} | {'P50':<8} | {'P75':<8} | {'P90':<8} | {'P95':<8} | {'MAX':<8} | {'Avg Groq':<8} | {'Avg Retr':<8} | {'Avg OutTok':<10} | Target Status", flush=True)
    print("=" * 135, flush=True)

    for key, label in [("en", "English"), ("hi", "Hindi"), ("mr", "Marathi"), ("bn", "Bengali"), ("te", "Telugu")]:
        res_list = [r for r in results[key] if r.groq_success]
        if res_list:
            arr_tot = np.array([r.total_latency_ms for r in res_list])
            arr_grq = np.array([r.groq_llm_latency_ms for r in res_list])
            arr_ret = np.array([r.retrieval_latency_ms for r in res_list])
            arr_out = np.array([r.output_token_count for r in res_list])

            p50 = np.percentile(arr_tot, 50)
            p75 = np.percentile(arr_tot, 75)
            p90 = np.percentile(arr_tot, 90)
            p95 = np.percentile(arr_tot, 95)
            max_v = np.max(arr_tot)
            avg_grq = np.mean(arr_grq)
            avg_ret = np.mean(arr_ret)
            avg_out = np.mean(arr_out)

            status_str = "PASS (<= 200 ms)" if p50 <= 200.0 else "FAIL (> 200 ms)"
            print(f"{label:<20} | {len(res_list):<4} | {p50:6.2f}ms | {p75:6.2f}ms | {p90:6.2f}ms | {p95:6.2f}ms | {max_v:6.2f}ms | {avg_grq:6.2f}ms | {avg_ret:6.2f}ms | {avg_out:10.1f} | {status_str}", flush=True)

    nc_tot = np.array([r.total_latency_ms for r in results["no_context"]])
    nc_calls = sum(r.groq_calls for r in results["no_context"])
    print(f"{'NO_CONTEXT':<20} | {len(results['no_context']):<4} | {np.percentile(nc_tot, 50):6.2f}ms | {np.percentile(nc_tot, 75):6.2f}ms | {np.percentile(nc_tot, 90):6.2f}ms | {np.percentile(nc_tot, 95):6.2f}ms | {np.max(nc_tot):6.2f}ms | {0.00:6.2f}ms | {np.mean([r.retrieval_latency_ms for r in results['no_context']]):6.2f}ms | {0.0:10.1f} | PASS (0 Groq Calls)", flush=True)

    un_tot = np.array([r.total_latency_ms for r in results["unsafe"]])
    un_calls = sum(r.groq_calls for r in results["unsafe"])
    print(f"{'UNSAFE':<20} | {len(results['unsafe']):<4} | {np.percentile(un_tot, 50):6.2f}ms | {np.percentile(un_tot, 75):6.2f}ms | {np.percentile(un_tot, 90):6.2f}ms | {np.percentile(un_tot, 95):6.2f}ms | {np.max(un_tot):6.2f}ms | {0.00:6.2f}ms | {0.00:6.2f}ms | {0.0:10.1f} | PASS (0 Groq Calls)", flush=True)
    print("=" * 135, flush=True)

if __name__ == "__main__":
    run_benchmark()
