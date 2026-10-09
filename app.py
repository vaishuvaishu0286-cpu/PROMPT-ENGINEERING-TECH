import time
from concurrent.futures import ThreadPoolExecutor

import streamlit as st

from llm import DETAIL_LEVELS, ask_llm, has_api_key
from prompt_templates import SHOT_TECHNIQUES, TECHNIQUES, build_prompt

st.set_page_config(page_title="PromptLens", page_icon="🔍", layout="wide")

DEFAULT_PICKS = {"Zero-Shot", "Chain-of-Thought"}
MAX_PARALLEL = 4

# ====================== STYLES ======================
# Graph-paper notebook look: ink navy, highlighter yellow, hard offset shadows.
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
    --ink: #0f1b3d;
    --paper: #f3f6fb;
    --grid: #dbe3f1;
    --line: #c3cee3;
    --mark: #ffe14d;
    --blue: #2f4bff;
    --muted: #55628a;
}

html, body, .stApp, button, input, textarea, select {
    font-family: 'IBM Plex Sans', sans-serif !important;
}

.stApp {
    background-color: var(--paper);
    background-image:
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 28px 28px;
    color: var(--ink);
}

header[data-testid="stHeader"] { background: transparent; }

.block-container {
    max-width: 1180px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

/* ---------- Hero ---------- */
.hero { margin-bottom: 2.2rem; max-width: 760px; }
.hero h1 {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    font-weight: 800;
    font-size: clamp(2.6rem, 6vw, 4.4rem);
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 0 0 0.9rem;
    color: var(--ink);
}
.hero p {
    font-size: 1.12rem;
    line-height: 1.6;
    color: var(--muted);
    margin: 0;
    max-width: 52ch;
}

/* ---------- Step headers ---------- */
.step {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 2rem 0 0.8rem;
}
.step-num {
    width: 30px; height: 30px;
    display: grid; place-items: center;
    background: var(--ink);
    color: var(--mark);
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: 0.95rem;
    border-radius: 6px;
}
.step-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700;
    font-size: 1.35rem;
    letter-spacing: -0.02em;
    color: var(--ink);
}

/* ---------- Inputs ---------- */
.stTextArea textarea {
    background: #ffffff !important;
    color: var(--ink) !important;
    border: 2px solid var(--ink) !important;
    border-radius: 6px !important;
    font-size: 1.02rem;
    line-height: 1.55;
}
.stTextArea textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 4px 4px 0 var(--blue) !important;
}
.stTextArea textarea::placeholder { color: #8a95b5 !important; }

/* Technique checkboxes as small notebook tags */
div[data-testid="stCheckbox"] {
    background: #ffffff;
    border: 2px solid var(--line);
    border-radius: 6px;
    padding: 0.55rem 0.8rem 0.45rem;
    margin-bottom: 0.2rem;
}
div[data-testid="stCheckbox"]:has(input:checked) {
    border-color: var(--ink);
    background: #fff9d6;
    box-shadow: 3px 3px 0 var(--ink);
}
div[data-testid="stCheckbox"] label p {
    font-weight: 600;
    color: var(--ink) !important;
}
.tech-desc {
    font-size: 0.8rem;
    color: var(--muted);
    margin: -0.15rem 0 0.7rem 0.2rem;
}

/* ---------- Primary button ---------- */
.stButton > button,
.stDownloadButton > button {
    border: 2px solid var(--ink);
    border-radius: 6px;
    background: #ffffff;
    color: var(--ink);
    font-weight: 600;
    padding: 0.6rem 1.2rem;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    width: 100%;
    background: var(--mark);
    color: var(--ink);
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    padding: 0.85rem 1rem;
    box-shadow: 5px 5px 0 var(--ink);
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    transform: translate(2px, 2px);
    box-shadow: 3px 3px 0 var(--ink);
    border-color: var(--ink);
    color: var(--ink);
}
.stButton > button p, .stDownloadButton > button p { color: inherit !important; }

/* ---------- Result cards ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 2px solid var(--ink) !important;
    border-radius: 6px !important;
    box-shadow: 5px 5px 0 var(--ink);
}
.tape {
    display: inline-block;
    background: var(--mark);
    color: var(--ink);
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: 1rem;
    padding: 0.2rem 0.7rem;
    border: 2px solid var(--ink);
    border-radius: 4px;
    margin-bottom: 0.4rem;
}
.tape-sub { font-size: 0.82rem; color: var(--muted); margin-bottom: 0.6rem; }
.meta {
    display: flex; gap: 1rem; flex-wrap: wrap;
    margin-top: 0.8rem; padding-top: 0.6rem;
    border-top: 2px dashed var(--line);
    font-size: 0.8rem; color: var(--muted); font-weight: 500;
}

/* ---------- Misc ---------- */
.key-box {
    background: #fff9d6;
    border: 2px solid var(--ink);
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 1.2rem;
}
.key-box code { background: #ffffff; padding: 0.1rem 0.4rem; border-radius: 4px; }
div[data-testid="stExpander"] {
    background: #ffffff;
    border: 2px solid var(--line);
    border-radius: 6px;
}
.empty {
    border: 2px dashed var(--line);
    border-radius: 6px;
    padding: 1.4rem;
    color: var(--muted);
    background: rgba(255, 255, 255, 0.6);
}

@media (prefers-reduced-motion: reduce) {
    * { transition: none !important; }
}
@media (max-width: 768px) {
    .block-container { padding-top: 1.2rem; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ====================== HELPERS ======================
def step(num: int, title: str) -> None:
    st.markdown(
        f'<div class="step"><div class="step-num">{num}</div>'
        f'<div class="step-title">{title}</div></div>',
        unsafe_allow_html=True,
    )


def run_one(tech: str, question: str, examples: str, detail: str, temp: float) -> dict:
    start = time.time()
    prompt = build_prompt(tech, question, examples)
    try:
        answer = ask_llm(prompt, detail, temp)
        error = None
    except Exception as exc:  # show the error on that card, keep the others
        answer, error = "", str(exc)
    return {
        "technique": tech,
        "prompt": prompt,
        "answer": answer,
        "error": error,
        "seconds": time.time() - start,
    }


def results_markdown(question: str, results: list) -> str:
    out = [f"# PromptLens comparison\n\n**Question:** {question}\n"]
    for r in results:
        body = r["answer"] if not r["error"] else f"_Error: {r['error']}_"
        out.append(f"\n---\n\n## {r['technique']}\n\n{body}\n")
    return "".join(out)


# ====================== HERO ======================
st.markdown(
    """
<div class="hero">
    <h1>PromptLens</h1>
    <p>Ask one question, try it with different prompt techniques, and read the
    answers side by side to see which style works best.</p>
</div>
""",
    unsafe_allow_html=True,
)

if not has_api_key():
    st.markdown(
        """
<div class="key-box"><b>API key missing.</b> Create a file named <code>.env</code>
next to <code>app.py</code> and add <code>GROQ_API_KEY=your_key</code>, then restart the app.
A template is in <code>.env.example</code>.</div>
""",
        unsafe_allow_html=True,
    )

# ====================== STEP 1: QUESTION ======================
step(1, "Write your question")
question = st.text_area(
    "Your question",
    height=130,
    placeholder="Example: Explain how a hash map works and when I should not use one.",
    label_visibility="collapsed",
)

# ====================== STEP 2: TECHNIQUES ======================
step(2, "Pick the techniques to compare")
names = list(TECHNIQUES.keys())
selected = []
cols = st.columns(3)
for i, name in enumerate(names):
    with cols[i % 3]:
        if st.checkbox(name, value=name in DEFAULT_PICKS, key=f"tech_{name}"):
            selected.append(name)
        st.markdown(
            f'<div class="tech-desc">{TECHNIQUES[name]["description"]}</div>',
            unsafe_allow_html=True,
        )

examples = ""
if any(t in SHOT_TECHNIQUES for t in selected):
    examples = st.text_area(
        "Examples for One-Shot / Few-Shot (optional)",
        height=120,
        placeholder="Q: What is 2+2?\nA: 4\n\nLeave empty and the AI will write its own examples first.",
    )

# ====================== STEP 3: TUNE + RUN ======================
step(3, "Set the answer style and run")
left, right = st.columns(2)
with left:
    detail = st.select_slider("Detail level", options=list(DETAIL_LEVELS.keys()), value="Medium")
with right:
    temperature = st.slider(
        "Creativity",
        0.0,
        1.0,
        0.7,
        0.05,
        help="Low = focused and repeatable. High = more varied and creative.",
    )

run = st.button("Compare answers", type="primary")

# ====================== RUN ======================
if run:
    if not question.strip():
        st.warning("Write a question in step 1 first.")
    elif not selected:
        st.warning("Pick at least one technique in step 2.")
    elif not has_api_key():
        st.error("No API key found. Add GROQ_API_KEY to your .env file and restart.")
    else:
        with st.spinner(f"Asking with {len(selected)} technique(s)..."):
            with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
                futures = [
                    pool.submit(run_one, t, question, examples, detail, temperature)
                    for t in selected
                ]
                st.session_state["results"] = [f.result() for f in futures]
        st.session_state["question"] = question

# ====================== RESULTS ======================
results = st.session_state.get("results")
if results:
    st.markdown("---")
    st.markdown(
        f'<div class="step"><div class="step-title">Results</div></div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Question: {st.session_state.get('question', '')}")

    for start in range(0, len(results), 3):
        row = results[start : start + 3]
        cols = st.columns(len(row))
        for col, r in zip(cols, row):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f'<span class="tape">{r["technique"]}</span>'
                        f'<div class="tape-sub">{TECHNIQUES[r["technique"]]["description"]}</div>',
                        unsafe_allow_html=True,
                    )
                    if r["error"]:
                        st.error(r["error"])
                    else:
                        st.markdown(r["answer"])
                        words = len(r["answer"].split())
                        st.markdown(
                            f'<div class="meta"><span>{words} words</span>'
                            f'<span>{r["seconds"]:.1f}s</span></div>',
                            unsafe_allow_html=True,
                        )
                    with st.expander("Prompt sent to the AI"):
                        st.code(r["prompt"], language=None)
        st.write("")

    st.download_button(
        "Download all answers (.md)",
        data=results_markdown(st.session_state.get("question", ""), results),
        file_name="promptlens_comparison.md",
        mime="text/markdown",
    )
else:
    st.markdown(
        '<div class="empty">Your answers will appear here, one card per technique.</div>',
        unsafe_allow_html=True,
    )