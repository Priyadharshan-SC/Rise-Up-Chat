"""
safety.py
---------
Safety check service for Solace AI.

This module is the FIRST step in the request pipeline. Any message
that triggers a crisis keyword is immediately flagged so the route
handler can return an emergency response without further processing.

Future ML integration:
    Replace (or augment) keyword matching with a fine-tuned text
    classifier (e.g., a DistilBERT model trained on crisis datasets)
    for higher recall and fewer false positives.
"""

from utils.helpers import normalise_text, contains_any_keyword

# ---------------------------------------------------------------------------
# Crisis keyword lists — extend as needed
# ---------------------------------------------------------------------------

# High-severity keywords: explicit self-harm / suicide intent
_CRISIS_KEYWORDS = [
    "suicide",
    "suicidal",
    "kill myself",
    "end my life",
    "take my life",
    "want to die",
    "wanna die",
    "going to die",
    "i will die",
    "self harm",
    "self-harm",
    "cut myself",
    "hurt myself",
    "no reason to live",
    "not worth living",
]

# Emergency response returned when a crisis keyword is detected
EMERGENCY_RESPONSE = (
    "I'm really concerned about what you've shared. "
    "Please know you are not alone. 💙\n\n"
    "Reach out to a crisis helpline right now:\n"
    "• iCall (India): 9152987821\n"
    "• AASRA: 9820466627\n"
    "• International Association for Suicide Prevention: "
    "https://www.iasp.info/resources/Crisis_Centres/\n\n"
    "A trained counsellor is ready to listen. You matter."
)


def check_safety(text: str) -> bool:
    """
    Determine whether a user message is safe (does not indicate a crisis).

    Args:
        text: The raw user input string.

    Returns:
        True  → message is safe to process normally.
        False → message contains crisis-level content; trigger emergency flow.
    """
    normalised = normalise_text(text)
    crisis_detected = contains_any_keyword(normalised, _CRISIS_KEYWORDS)

    # Safe = no crisis keyword found
    return not crisis_detected
