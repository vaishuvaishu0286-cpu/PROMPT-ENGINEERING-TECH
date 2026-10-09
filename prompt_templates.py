"""Prompt-engineering techniques used by PromptLens."""

TECHNIQUES = {
    "Zero-Shot": {
        "description": "Ask directly, no examples.",
        "instruction": "Answer the user's question clearly and directly, without relying on examples.",
    },
    "One-Shot": {
        "description": "One example shows the format.",
        "instruction": "Follow the single example below as a guide for the format and style of your answer.",
        "shots": 1,
    },
    "Few-Shot": {
        "description": "Several examples set the pattern.",
        "instruction": "Learn the pattern from the examples below and apply it to the user's question.",
        "shots": 3,
    },
    "Role-Based": {
        "description": "The AI plays a specific expert.",
        "instruction": "Act as a knowledgeable expert in the field of the user's question and answer in that voice.",
    },
    "Chain-of-Thought": {
        "description": "Reason step by step.",
        "instruction": "Break the problem into clear steps, show the reasoning for each, then state the conclusion.",
    },
    "Tree-of-Thought": {
        "description": "Explore several paths, pick the best.",
        "instruction": (
            "Explore three different approaches to the problem. Briefly evaluate the strengths and "
            "weaknesses of each, then choose the best one and give the final answer."
        ),
    },
    "Structured Output": {
        "description": "Headings, bullets, tables.",
        "instruction": "Organize the answer with suitable headings, bullet points or a numbered list.",
    },
    "Constraint-Based": {
        "description": "Follow strict rules you set.",
        "instruction": "Follow every constraint in the user's request exactly (length, tone, language, format).",
    },
    "Beginner-Friendly": {
        "description": "Plain words, simple examples.",
        "instruction": "Explain from beginner level using simple words, short sentences and everyday examples.",
    },
}

# Techniques that take examples from the user
SHOT_TECHNIQUES = [name for name, t in TECHNIQUES.items() if "shots" in t]


def build_prompt(technique: str, user_prompt: str, examples: str = "") -> str:
    selected = TECHNIQUES.get(technique)
    if not selected:
        raise ValueError(f"Unknown prompt technique: {technique}")

    parts = [
        f"Prompt Engineering Technique: {technique}",
        f"Instruction: {selected['instruction']}",
    ]

    shots = selected.get("shots")
    if shots:
        examples = (examples or "").strip()
        if examples:
            parts.append(f"Examples:\n{examples}")
        else:
            word = "example" if shots == 1 else "examples"
            parts.append(
                f"No examples were supplied. First write {shots} short {word} of a similar "
                "question and answer in the format you will use, then answer the real question."
            )

    parts.append(f"User Request:\n{user_prompt.strip()}")
    parts.append("Provide a helpful, accurate and well-organized response.")
    return "\n\n".join(parts)