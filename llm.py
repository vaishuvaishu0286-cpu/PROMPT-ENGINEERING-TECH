import os
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).parent
ENV_NAMES = (".env", "_env", ".env.txt")

for _name in ENV_NAMES:
    if (HERE / _name).exists():
        load_dotenv(dotenv_path=HERE / _name, override=True)


def _clean(name: str) -> str:
    return (os.getenv(name) or "").strip().strip('"').strip("'")


GROQ_MODEL = _clean("GROQ_MODEL") or "openai/gpt-oss-120b"
HF_MODEL = _clean("HF_MODEL") or "Qwen/Qwen2.5-72B-Instruct"

# Response detail levels: (max_tokens, instruction)
DETAIL_LEVELS = {
    "Short": (700, "Keep the answer concise but complete."),
    "Medium": (1800, "Give a clear and well-explained answer."),
    "Detailed": (
        3500,
        "Give a thorough answer with explanations, examples, headings and bullet points.",
    ),
    "Very Detailed": (
        6000,
        "Give a comprehensive answer covering background, steps, examples, edge cases and summary.",
    ),
}

PREAMBLE = (
    "You are a helpful expert assistant. "
    "Write accurate and well-structured answers in Markdown. "
    "{detail}\n\n"
)


def has_api_key() -> bool:
    return bool(_clean("GROQ_API_KEY") or _clean("HF_TOKEN"))


def ask_llm(prompt: str, detail: str = "Detailed", temperature: float = 0.7) -> str:
    max_tokens, instruction = DETAIL_LEVELS.get(detail, DETAIL_LEVELS["Detailed"])
    messages = [{"role": "user", "content": PREAMBLE.format(detail=instruction) + prompt}]

    groq_key = _clean("GROQ_API_KEY")
    hf_token = _clean("HF_TOKEN")

    # Option 1: Groq
    if groq_key:
        from groq import Groq

        client = Groq(api_key=groq_key)

        def _call(model):
            return client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

        try:
            response = _call(GROQ_MODEL)
        except Exception as e:
            if "model_not_found" not in str(e) and "does not exist" not in str(e):
                raise
            # Chosen model unavailable -> pick one this key can use
            skip = ("whisper", "orpheus", "guard", "tts", "embed", "compound")
            ids = [m.id for m in client.models.list().data]
            usable = [i for i in ids if not any(k in i.lower() for k in skip)]
            if not usable:
                raise
            prefer = [i for i in usable if "gpt-oss-120b" in i] or usable
            response = _call(prefer[0])
        return (response.choices[0].message.content or "").strip()

    # Option 2: Hugging Face
    if hf_token:
        from huggingface_hub import InferenceClient

        response = InferenceClient(model=HF_MODEL, token=hf_token).chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=max(temperature, 0.01),
        )
        return (response.choices[0].message.content or "").strip()

    found = [n for n in ENV_NAMES if (HERE / n).exists()]
    raise ValueError(
        "No API key found. Create a file named .env next to app.py and add "
        f"GROQ_API_KEY=your_key. Looked in: {HERE} | env files found: {found or 'NONE'}"
    )