import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

print("ENVIRONMENT KEYS PROBE:")
for k in ["GROQ_API_KEY", "GEMINI_API_KEY", "CEREBRAS_API_KEY", "FIREWORKS_API_KEY", "SAMBANOVA_API_KEY", "TOGETHER_API_KEY", "OPENAI_API_KEY"]:
    val = os.getenv(k)
    print(f"  {k:<20}: {'SET (' + val[:8] + '...)' if val else 'UNSET'}")
