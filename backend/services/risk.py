"""
risk.py
-------
Risk level classifier for Solace AI.

Assigns one of four risk tiers to each message:
    crisis  → safety check already failed (self-harm keywords)
    high    → strong distress signals (sad/anxious + negative intensifiers)
    medium  → mild distress detected
    low     → normal / positive / neutral
"""

from utils.helpers import normalise_text, contains_any_keyword

# Words that intensify the severity of distress when paired with sad/anxious emotion
_HIGH_RISK_WORDS = [
    "hopeless", "worthless", "trapped", "alone", "empty",
    "pointless", "meaningless", "nobody cares", "no one cares",
    "can't breathe", "cant breathe", "breaking down",
    "falling apart", "give up", "giving up", "no way out",
    "can't go on", "cant go on", "exhausted", "numb",
    # Grief-related expressions that can mask suicidal ideation
    "join her", "join him", "join them",
    "be with her", "be with him", "be with them",
    "follow her", "follow him",
    "see her again", "see him again",
    "be by her side", "be by his side",
    "miss her so much", "miss him so much",
    "cant live without", "can't live without",
    "died inside", "dead inside", "wish i was gone",
]

_MEDIUM_RISK_WORDS = [
    "overwhelmed", "stressed", "anxious", "worried", "scared",
    "nervous", "sad", "depressed", "unhappy", "miserable",
    "struggling", "lost", "confused", "upset", "frustrated",
    "lonely", "tired", "burnt out", "burned out",
]


def classify_risk(
    text: str,
    emotion: str,
    confidence: float,
    is_safe: bool,
) -> str:
    """
    Determine the risk level of a message.

    Args:
        text:       The raw user input.
        emotion:    Detected emotion label ("sad", "anxious", etc.).
        confidence: Model confidence (0.0 – 1.0).
        is_safe:    Result of the safety check (False = crisis keywords present).

    Returns:
        One of: "crisis" | "high" | "medium" | "low"
    """
    if not is_safe:
        return "crisis"

    normalised = normalise_text(text)

    # High risk: distress emotion with high confidence AND at least one intensifier
    if emotion in ("sad", "anxious") and confidence >= 0.65:
        if contains_any_keyword(normalised, _HIGH_RISK_WORDS):
            return "high"

    # Medium risk: distress emotion OR medium-risk vocabulary detected
    if emotion in ("sad", "anxious", "angry"):
        return "medium"

    if contains_any_keyword(normalised, _MEDIUM_RISK_WORDS):
        return "medium"

    return "low"
