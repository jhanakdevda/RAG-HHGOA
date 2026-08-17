import os
import sys
import torch
import requests
from dotenv import load_dotenv

load_dotenv()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

print("LOCAL ENVIRONMENT PROBE:")
print(f"  PyTorch Installed  : {torch.__version__}")
print(f"  CUDA Available     : {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  CUDA Device Name   : {torch.cuda.get_device_name(0)}")
    print(f"  CUDA Memory Alloc  : {torch.cuda.memory_allocated(0)/(1024**2):.2f} MB")

# Check Ollama local service
ollama_running = False
try:
    resp = requests.get("http://localhost:11434/api/tags", timeout=2.0)
    if resp.status_code == 200:
        ollama_running = True
        models = resp.json().get("models", [])
        print(f"  Ollama Service     : RUNNING (Models: {[m['name'] for m in models]})")
    else:
        print(f"  Ollama Service     : RESPONDED status {resp.status_code}")
except Exception as e:
    print(f"  Ollama Service     : NOT RUNNING ({e})")
