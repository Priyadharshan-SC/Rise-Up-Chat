"""
emotion.py
----------
Emotion detection service for Solace AI.

Implements a rule-based classifier that maps user messages to one of
four emotional states. The design is intentionally extensible — the
keyword dictionaries can be expanded or replaced wholesale with an
ML model (e.g., a transformer fine-tuned on SemEval emotion data).

Supported emotions:
    sad       → sadness / depression signals
    anxious   → stress / anxiety signals
    angry     → anger / frustration signals
    happy     → joy / positive signals
    neutral   → default when no match is found
"""

from typing import Dict, List
from utils.helpers import normalise_text, contains_any_keyword

# ---------------------------------------------------------------------------
# Keyword vocabularies — order matters; first match wins
# ---------------------------------------------------------------------------

_EMOTION_KEYWORDS: Dict[str, List[str]] = {
    "sad": [
        "sad", "sadness", "depressed", "depression", "unhappy",
        "cry", "crying", "tears", "hopeless", "miserable",
        "heartbroken", "grief", "lonely", "alone", "empty",
        "worthless", "numb", "broken",
    ],
    "anxious": [
        "anxious", "anxiety", "stress", "stressed", "stressful",
        "nervous", "panic", "panicking", "overwhelmed", "worried",
        "worry", "fear", "fearful", "scared", "terrified",
        "restless", "uneasy", "tense",
    ],
    "angry": [
        "angry", "anger", "furious", "rage", "mad",
        "frustrated", "frustration", "irritated", "annoyed",
        "hate", "hatred", "disgusted", "outraged", "resentful",
    ],
    "happy": [
        "happy", "happiness", "joyful", "joy", "excited",
        "grateful", "thankful", "wonderful", "great", "amazing",
        "fantastic", "elated", "content", "pleased", "cheerful",
    ],
}

# Neutral is the fallback — no dedicated keywords needed
_DEFAULT_EMOTION = "neutral"


def detect_emotion(text: str) -> str:
    """
    Classify the dominant emotion expressed in *text*.

    Iterates through emotion categories in priority order.
    The first matching category is returned.

    Args:
        text: The raw user input string.

    Returns:
        One of: "sad", "anxious", "angry", "happy", "neutral".

    Future ML integration:
        return emotion_model.predict(text)  # drop-in replacement
    """
    normalised = normalise_text(text)

    for emotion, keywords in _EMOTION_KEYWORDS.items():
        if contains_any_keyword(normalised, keywords):
            return emotion

    return _DEFAULT_EMOTION
