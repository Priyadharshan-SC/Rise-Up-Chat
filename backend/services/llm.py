"""
llm.py
------
Local LLM integration service for Solace AI.

Stateless response generator using Ollama (solace-llama3).
Short-term memory: injects the last 2 conversation turns into the prompt.
No personal data or full DB history is ever sent to the model.
"""

import requests
from typing import List, Dict, Any

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "solace-llama3"


def generate_llm_response(
    emotion: str,
    text: str,
    context: List[Dict[str, str]] | None = None,
) -> str | None:
    """
    Generate an empathetic response via the local LLM.

    Args:
        emotion:  Detected emotion label.
        text:     The current user message.
        context:  Up to 2 recent turns as [{"user": ..., "bot": ...}, ...]

    Returns:
        Generated text string, or None if the call fails.
    """

    # ── Build short-term memory block ────────────────────────────────────────
    memory_block = ""
    if context:
        lines = []
        for turn in context:
            lines.append(f"User: {turn['user']}")
            lines.append(f"Bot: {turn['bot']}")
        memory_block = "Recent context:\n" + "\n".join(lines) + "\n\n"

    # ── Controlled prompt ─────────────────────────────────────────────────────
    prompt = (
        "You are an empathetic mental wellness assistant.\n"
        "Your goal is to provide a single, supportive, validating, and safe response.\n"
        "Keep your response concise (3-5 sentences). Do not use generic AI intros.\n\n"
        f"{memory_block}"
        f"Emotion: {emotion}\n"
        f"User message: {text}\n\n"
        "Respond in a safe, supportive, and helpful way:"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.6},
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip() or None

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Local LLM unavailable or failed: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error during LLM generation: {e}")
        return None
