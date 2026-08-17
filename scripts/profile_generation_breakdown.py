"""
Phase 5B: Fine-Grained Groq Generation Latency Profiler
Measures network request setup, TTFT, token generation rate (ms/token), and complete stream latency.
"""

import os
import sys
import time
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.config import get_settings
from app.rag.llm.factory import get_llm_provider
from app.rag.prompts import SYSTEM_GROUNDING_PROMPT
from app.rag.guardrails.injection import InjectionDefense
from app.models.chunk import TextChunk


def run_generation_profiling():
    print("=" * 90, flush=True)
    print("PHASE 5B — GROQ FINE-GRAINED GENERATION LATENCY PROFILING", flush=True)
    print("=" * 90, flush=True)

    settings = get_settings()
    model_name = settings.llm_model
    provider = get_llm_provider()

    print(f"Active LLM Model : {model_name}", flush=True)
    print(f"Provider Class   : {provider.__class__.__name__}\n", flush=True)

    test_context = [
        TextChunk(
            chunk_id="chk_101",
            query_id=200,
            text="Eagles fly at typical cruising speeds between 30 and 55 miles per hour. When diving for prey, bald eagles can reach speeds of over 100 miles per hour.",
            passage_index=0,
            chunk_index=0,
            char_count=160,
            word_count=29,
            language_code="en"
        )
    ]
    query_str = "How fast do eagles fly?"

    context_blocks_str = InjectionDefense.format_untrusted_context(test_context)
    untrusted_query_str = InjectionDefense.format_untrusted_query(query_str)
    system_prompt = SYSTEM_GROUNDING_PROMPT.format(
        target_language="en",
        context_blocks=context_blocks_str,
        user_query=untrusted_query_str
    )

    client = provider._get_client()

    num_runs = 5
    ttft_list = []
    complete_list = []
    token_count_list = []
    ms_per_token_list = []
    inter_token_delays = []

    print(f"Executing {num_runs} warm streaming generation profiling runs...\n", flush=True)

    for i in range(num_runs):
        if i > 0:
            time.sleep(6.0)  # Pause to respect Groq TPM

        t0 = time.perf_counter()

        # Step 1: Request payload construction
        t_req_start = time.perf_counter()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please answer the user's question based strictly on the context:\n\n{untrusted_query_str}"}
        ]
        t_req_const = (time.perf_counter() - t_req_start) * 1000.0

        # Step 2: Stream API Call & TTFT Timing
        t_stream_start = time.perf_counter()
        stream_resp = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.1,
            max_tokens=90,
            stream=True
        )

        first_token = True
        ttft_ms = 0.0
        chunks = []
        token_times = []

        for chunk in stream_resp:
            now = time.perf_counter()
            if chunk.choices and chunk.choices[0].delta.content:
                text_delta = chunk.choices[0].delta.content
                token_times.append((now - t_stream_start) * 1000.0)
                chunks.append(text_delta)
                if first_token:
                    ttft_ms = (now - t_stream_start) * 1000.0
                    first_token = False

        t_complete = (time.perf_counter() - t_stream_start) * 1000.0
        full_text = "".join(chunks)
        token_cnt = len(chunks)

        gen_time_after_first_token = t_complete - ttft_ms
        ms_per_token = (gen_time_after_first_token / max(1, token_cnt - 1)) if token_cnt > 1 else 0.0

        ttft_list.append(ttft_ms)
        complete_list.append(t_complete)
        token_count_list.append(token_cnt)
        ms_per_token_list.append(ms_per_token)

        print(f"Run #{i+1:02d} | TTFT: {ttft_ms:6.2f} ms | Complete Stream: {t_complete:6.2f} ms | Tokens: {token_cnt:3d} | Rate: {ms_per_token:5.2f} ms/token", flush=True)
        print(f"  Output: '{full_text[:75]}...'\n", flush=True)

    print("=" * 90, flush=True)
    print("GROQ GENERATION BREAKDOWN SUMMARY (5 WARM RUNS)", flush=True)
    print("=" * 90, flush=True)
    print(f"Model Identifier                 : {model_name}", flush=True)
    print(f"TTFT P50                         : {np.percentile(ttft_list, 50):7.2f} ms", flush=True)
    print(f"TTFT P95                         : {np.percentile(ttft_list, 95):7.2f} ms", flush=True)
    print(f"Complete Generation P50          : {np.percentile(complete_list, 50):7.2f} ms", flush=True)
    print(f"Complete Generation P95          : {np.percentile(complete_list, 95):7.2f} ms", flush=True)
    print(f"Inter-token Rate P50             : {np.percentile(ms_per_token_list, 50):7.2f} ms/token", flush=True)
    print(f"Token Count P50                  : {int(np.percentile(token_count_list, 50))} tokens", flush=True)
    print("=" * 90, flush=True)


if __name__ == "__main__":
    run_generation_profiling()
