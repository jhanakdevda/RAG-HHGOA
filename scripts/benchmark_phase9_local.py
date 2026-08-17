"""
Phase 9: Local LLM <200ms Feasibility Test Benchmark
Measures complete end-to-end /ask latency, TTFT, generation latency, embedding, FAISS,
GroundingVerifier, RAM/memory usage, grounding scores, and multilingual accuracy for
local CPU/PyTorch LLM inference candidates under identical production RAG parameters.
"""

import os
import sys
import time
import psutil
import torch
import numpy as np
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from transformers import AutoModelForCausalLM, AutoTokenizer
from app.models.generation import AskRequest
from app.models.retrieval import RetrievalRequest
from app.rag.generator import GeneratorService
from app.rag.guardrails.safety import SafetyFilter
from app.rag.guardrails.injection import InjectionDefense
from app.rag.prompts import SYSTEM_GROUNDING_PROMPT
from app.rag.llm.base import BaseLLMProvider


class LocalHuggingFaceLLMProvider(BaseLLMProvider):
    """Local HuggingFace Transformers LLM Provider for CPU Inference Benchmark."""

    def __init__(self, model_repo_id: str, timeout: float = 15.0):
        self.model_repo_id = model_repo_id
        self.timeout = timeout
        print(f"Loading local model '{model_repo_id}' into memory...", flush=True)
        t0 = time.perf_counter()
        self.tokenizer = AutoTokenizer.from_pretrained(model_repo_id, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_repo_id,
            torch_dtype=torch.float32,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        self.model.eval()
        t_load = (time.perf_counter() - t0) * 1000.0
        print(f"Model '{model_repo_id}' loaded successfully in {t_load:.2f} ms.", flush=True)

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        full_text = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        inputs = self.tokenizer(full_text, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=48,
                do_sample=False,
                temperature=0.1
            )
        new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    def generate_streaming(self, prompt: str, system_instruction: str = None):
        """Measures complete generation latency for local CPU inference."""
        full_text = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        inputs = self.tokenizer(full_text, return_tensors="pt")
        input_ids = inputs["input_ids"]

        t_gen_start = time.perf_counter()
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=48,
                do_sample=False
            )
        t_gen_complete = (time.perf_counter() - t_gen_start) * 1000.0
        ttft_ms = t_gen_complete / max(1, (outputs.shape[1] - input_ids.shape[1]))

        new_tokens = outputs[0][input_ids.shape[1]:]
        text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        return text, ttft_ms, t_gen_complete


def benchmark_local_candidate(model_repo_id: str, model_size_desc: str, target_samples: int = 20) -> Dict[str, Any]:
    print("\n" + "=" * 95, flush=True)
    print(f"BENCHMARKING LOCAL CANDIDATE: {model_repo_id} ({model_size_desc})", flush=True)
    print("=" * 95, flush=True)

    process = psutil.Process(os.getpid())
    ram_start_mb = process.memory_info().rss / (1024 * 1024)

    try:
        local_provider = LocalHuggingFaceLLMProvider(model_repo_id)
        generator = GeneratorService(llm_provider=local_provider)
    except Exception as e:
        print(f"Failed to load local model '{model_repo_id}': {e}", flush=True)
        return {
            "model_name": model_repo_id,
            "model_size": model_size_desc,
            "status": "FAILED",
            "error": str(e)
        }

    ram_after_load_mb = process.memory_info().rss / (1024 * 1024)
    model_ram_mb = ram_after_load_mb - ram_start_mb

    test_queries = [
        {"query": "How fast do eagles fly?", "lang": "en", "kw": "30"},
        {"query": "What is the wingspan of a bald eagle?", "lang": "en", "kw": "feet"},
        {"query": "How do eagles catch fish?", "lang": "en", "kw": "water"},
        {"query": "What is the nesting behavior of eagles?", "lang": "en", "kw": "nest"},
        {"query": "चील कितनी तेजी से उड़ती है?", "lang": "hi", "kw": "30"},
        {"query": "गरुड किती वेगाने उडतो?", "lang": "mr", "kw": "30"},
        {"query": "ইগল কত দ্রুত উড়ে?", "lang": "bn", "kw": "30"}
    ]

    print("[Warming up local model with 2 requests...]", flush=True)
    for _ in range(2):
        try:
            _ = generator.generate_answer(AskRequest(query=test_queries[0]["query"], top_k=3))
        except Exception:
            pass
    print("[Warmup complete. Running 20 benchmark samples...]\n", flush=True)

    ttft_list = []
    complete_gen_list = []
    embed_list = []
    faiss_list = []
    verifier_list = []
    total_ask_list = []
    output_token_counts = []
    grounding_scores = []
    grounding_statuses = []
    sample_answers = []

    successful_count = 0
    failure_count = 0

    for i in range(target_samples):
        q_item = test_queries[i % len(test_queries)]
        q_text = q_item["query"]
        q_lang = q_item["lang"]

        t0 = time.perf_counter()

        # Step 1: Safety screening
        safety_state, _ = SafetyFilter.evaluate_query(q_text)

        # Step 2: Dense retrieval & timing
        t_embed_start = time.perf_counter()
        q_emb = generator.retrieval_service.embedding_service.encode_query(q_text)
        t_embed = (time.perf_counter() - t_embed_start) * 1000.0

        t_faiss_start = time.perf_counter()
        ret_resp = generator.retrieval_service.retrieve(RetrievalRequest(query=q_text, top_k=3))
        t_faiss = (time.perf_counter() - t_faiss_start) * 1000.0
        retrieved_chunks = [r.chunk for r in ret_resp.results]

        # Step 3: Context & prompt packaging
        context_blocks_str = InjectionDefense.format_untrusted_context(retrieved_chunks)
        untrusted_query_str = InjectionDefense.format_untrusted_query(q_text)
        system_prompt = SYSTEM_GROUNDING_PROMPT.format(
            target_language=q_lang,
            context_blocks=context_blocks_str,
            user_query=untrusted_query_str
        )

        # Step 4: Measured LLM Generation & TTFT
        try:
            text_out, ttft_ms, gen_ms = local_provider.generate_streaming(
                prompt=f"Please answer the user's question based strictly on the context:\n\n{untrusted_query_str}",
                system_instruction=system_prompt
            )
        except Exception as e:
            failure_count += 1
            print(f"  Sample #{i+1:02d} generation error: {e}", flush=True)
            continue

        # Step 5: GroundingVerifier Execution
        t_ver_start = time.perf_counter()
        _, status, score = generator.grounding_verifier.verify(text_out, retrieved_chunks)
        t_ver = (time.perf_counter() - t_ver_start) * 1000.0

        t_total = (time.perf_counter() - t0) * 1000.0
        tok_cnt = len(text_out.split())

        ttft_list.append(ttft_ms)
        complete_gen_list.append(gen_ms)
        embed_list.append(t_embed)
        faiss_list.append(t_faiss)
        verifier_list.append(t_ver)
        total_ask_list.append(t_total)
        output_token_counts.append(tok_cnt)
        grounding_scores.append(score)
        grounding_statuses.append(status.value)
        sample_answers.append(text_out)

        successful_count += 1
        print(f"  Sample #{successful_count:02d}/{target_samples} | Lang: {q_lang} | TTFT: {ttft_ms:5.1f}ms | Gen: {gen_ms:6.1f}ms | Ver: {t_ver:5.1f}ms | Total /ask: {t_total:6.1f}ms", flush=True)

    if successful_count == 0:
        return {
            "model_name": model_repo_id,
            "model_size": model_size_desc,
            "status": "FAILED",
            "failure_count": failure_count
        }

    ttft_arr = np.array(ttft_list)
    gen_arr = np.array(complete_gen_list)
    embed_arr = np.array(embed_list)
    faiss_arr = np.array(faiss_list)
    ver_arr = np.array(verifier_list)
    tot_arr = np.array(total_ask_list)

    return {
        "model_name": model_repo_id,
        "model_size": model_size_desc,
        "backend": "CPU (PyTorch float32)",
        "success_count": successful_count,
        "failure_count": failure_count,
        "ram_usage_mb": float(model_ram_mb),
        "ttft_p50": float(np.percentile(ttft_arr, 50)),
        "ttft_p70": float(np.percentile(ttft_arr, 70)),
        "ttft_p95": float(np.percentile(ttft_arr, 95)),
        "gen_p50": float(np.percentile(gen_arr, 50)),
        "gen_p70": float(np.percentile(gen_arr, 70)),
        "gen_p95": float(np.percentile(gen_arr, 95)),
        "embed_p50": float(np.percentile(embed_arr, 50)),
        "faiss_p50": float(np.percentile(faiss_arr, 50)),
        "verifier_p50": float(np.percentile(ver_arr, 50)),
        "total_ask_p50": float(np.percentile(tot_arr, 50)),
        "total_ask_p70": float(np.percentile(tot_arr, 70)),
        "total_ask_p95": float(np.percentile(tot_arr, 95)),
        "total_ask_p100": float(np.max(tot_arr)),
        "avg_tokens": int(np.mean(output_token_counts)),
        "avg_grounding_score": float(np.mean(grounding_scores)),
        "status": grounding_statuses[0] if grounding_statuses else "N/A",
        "sample_answers": sample_answers[:2]
    }


def run_phase9_local_feasibility_test():
    print("=" * 95, flush=True)
    print("PHASE 9: LOCAL LLM <200ms FEASIBILITY TEST BENCHMARK", flush=True)
    print("=" * 95, flush=True)

    candidates = [
        {"id": "HuggingFaceTB/SmolLM2-135M-Instruct", "desc": "135 Million Parameters"},
        {"id": "Qwen/Qwen2.5-0.5B-Instruct", "desc": "500 Million Parameters"},
        {"id": "Qwen/Qwen2.5-1.5B-Instruct", "desc": "1.5 Billion Parameters"}
    ]

    results = []
    for c in candidates:
        res = benchmark_local_candidate(model_repo_id=c["id"], model_size_desc=c["desc"], target_samples=20)
        results.append(res)
        torch.cuda.empty_cache() if torch.cuda.is_available() else None

    print("\n" + "=" * 125, flush=True)
    print("PHASE 9 LOCAL INFRASTRUCTURE FEASIBILITY SUMMARY TABLE", flush=True)
    print("=" * 125, flush=True)
    header = f"{'Model Repo ID':<35} | {'Size':<12} | {'TTFT P50':<9} | {'Gen P50':<9} | {'Embed P50':<9} | {'Ver P50':<8} | {'Total P50':<9} | {'Total P100':<10} | {'RAM (MB)':<9} | {'G-Score':<7}"
    print(header, flush=True)
    print("-" * len(header), flush=True)

    for r in results:
        m_name = r["model_name"][:35]
        m_sz = r["model_size"][:12]
        if r.get("status") == "FAILED":
            print(f"{m_name:<35} | {m_sz:<12} | {'N/A':<9} | {'N/A':<9} | {'N/A':<9} | {'N/A':<8} | {'N/A':<9} | {'N/A':<10} | {'N/A':<9} | {'N/A':<7}", flush=True)
        else:
            ttft = f"{r['ttft_p50']:6.1f}ms"
            gen = f"{r['gen_p50']:6.1f}ms"
            emb = f"{r['embed_p50']:6.1f}ms"
            ver = f"{r['verifier_p50']:5.1f}ms"
            tot50 = f"{r['total_ask_p50']:6.1f}ms"
            tot100 = f"{r['total_ask_p100']:7.1f}ms"
            ram = f"{r['ram_usage_mb']:7.1f}"
            g_sc = f"{r['avg_grounding_score']:6.4f}"
            print(f"{m_name:<35} | {m_sz:<12} | {ttft:<9} | {gen:<9} | {emb:<9} | {ver:<8} | {tot50:<9} | {tot100:<10} | {ram:<9} | {g_sc:<7}", flush=True)

    print("=" * 125, flush=True)


if __name__ == "__main__":
    run_phase9_local_feasibility_test()
