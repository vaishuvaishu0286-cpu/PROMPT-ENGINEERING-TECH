"""Quick check: does your key work and which Groq models can you use?"""
from llm import _clean, has_api_key

if not has_api_key():
    raise SystemExit("No key found. Copy .env.example to .env and add GROQ_API_KEY.")

from groq import Groq

for m in Groq(api_key=_clean("GROQ_API_KEY")).models.list().data:
    print(m.id)