# PromptLens

Ask one question, try it with different prompt-engineering techniques, and read the answers side by side to see which style works best.

Built with Python, Streamlit, and the Groq API (Hugging Face as a fallback).

## What it does

1. You write a question.
2. You pick the techniques to compare (Zero-Shot, Few-Shot, Chain-of-Thought, and more).
3. You set the detail level and creativity, then press **Compare answers**.
4. You get one card per technique, showing the answer, word count, response time, and the exact prompt that was sent.
5. You can download all answers as a Markdown file.

https://prompt-engineering-tech-bxbjyhckgxfn26qq9rbguj.streamlit.app

## Techniques included

| Technique | Idea |
|---|---|
| Zero-Shot | Ask directly, no examples |
| One-Shot | One example shows the format |
| Few-Shot | Several examples set the pattern |
| Role-Based | The AI plays a specific expert |
| Chain-of-Thought | Reason step by step |
| Tree-of-Thought | Explore several paths, pick the best |
| Structured Output | Headings, bullets, tables |
| Constraint-Based | Follow strict rules you set |
| Beginner-Friendly | Plain words, simple examples |

For One-Shot and Few-Shot you can paste your own examples. If you leave the box empty, the AI writes its own examples first.

## Project structure

```
promptlens/
├── app.py                # Streamlit UI
├── llm.py                # API calls (Groq, Hugging Face fallback)
├── prompt_templates.py   # Technique definitions and prompt builder
├── test.py               # Checks your key and lists usable models
├── requirements.txt
├── .env.example          # Template for your API key
└── .streamlit/
    └── config.toml       # Theme colors
```

## Setup

**1. Install Python 3.9 or newer**, then open a terminal in the project folder.

**2. Install the packages**

```
pip install -r requirements.txt
```

**3. Add your API key**

Get a free key at https://console.groq.com/keys

Copy the template to a real `.env` file:

```
copy .env.example .env        # Windows
cp .env.example .env          # Mac / Linux
```

Open `.env` and replace the placeholder:

```
GROQ_API_KEY=gsk_your_real_key_here
```

No spaces around `=`, no quotes. The file must be named exactly `.env` and sit next to `app.py`.

**4. Run the app**

```
streamlit run app.py
```

It opens at http://localhost:8501.

## Optional settings

Add these to `.env` if you want to change the defaults:

```
GROQ_MODEL=openai/gpt-oss-120b
HF_TOKEN=your_huggingface_token
HF_MODEL=Qwen/Qwen2.5-72B-Instruct
```

If `GROQ_API_KEY` is set, Groq is used. Otherwise the app falls back to Hugging Face when `HF_TOKEN` is set.

## Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'prompt_templates'` | The file must be named `prompt_templates.py` with an underscore, no spaces |
| "API key missing" box on the page | `.env` is missing, misnamed, or in the wrong folder. Restart the app after fixing it |
| Key is set but nothing works | Run `python test.py`. If it lists model names, the key is fine |
| Model not found error | Change `GROQ_MODEL` in `.env` to one listed by `python test.py` |
| `.env` shows as `.env.txt` | In File Explorer turn on **View > Show > File name extensions** and remove `.txt` |
| Changed `.env` but nothing changed | Stop the app with Ctrl+C and run it again |

## Security

Never share your `.env` file or post your API key online. If you send this folder to someone, delete `.env` first. If you use Git, add `.env` to `.gitignore`.

## Customize

- **Add a technique:** add a new entry to `TECHNIQUES` in `prompt_templates.py`. It appears in the app automatically.
- **Change detail levels:** edit `DETAIL_LEVELS` in `llm.py`.
- **Change colors:** edit the CSS variables at the top of the style block in `app.py`, and `.streamlit/config.toml`.
