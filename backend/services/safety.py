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
    "better off dead",
    "better off without me",
    "ready to die",
    "wish i was dead",
    "wish i were dead",
]

# High-risk phrases extracted from real-world distress datasets
_CRISIS_PHRASES = [
    "i'm done",
    "im done",
    "can't take this anymore",
    "cant take this anymore",
    "want to disappear",
    "wanna disappear",
    "end it all",
    "crash my car",
    "tired of living",
    "hate my life",
    "dont want to be here anymore",
    "don't want to be here anymore",
    "don't want to live",
    "dont want to live",
    "sick and tired of everything",
    "want to go to sleep and never wake up",
    "nothing to live for",
    # Grief-related suicidal ideation — joining / following a deceased person
    "gonna join her",
    "gonna join him",
    "gonna join them",
    "going to join her",
    "going to join him",
    "going to join them",
    "join her soon",
    "join him soon",
    "join them soon",
    "meet her again",
    "meet him again",
    "be with her forever",
    "be with him forever",
    "follow her",
    "follow him",
    "join her in heaven",
    "join him in heaven",
    "see her again soon",
    "see him again soon",
    "be by her side again",
    "be by his side again",
    # General death-wish phrases
    "i don't want to be alive",
    "i dont want to be alive",
    "no point being alive",
    "life is not worth it",
    "can't do this anymore",
    "cant do this anymore",
    "done with life",
    "done with everything",
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
    
    # Check both keywords and multi-word phrases
    crisis_detected = contains_any_keyword(normalised, _CRISIS_KEYWORDS) or \
                      contains_any_keyword(normalised, _CRISIS_PHRASES)

    # Safe = no crisis keyword found
    return not crisis_detected
