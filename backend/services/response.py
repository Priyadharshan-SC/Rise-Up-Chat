"""
response.py
-----------
Response generation service for Solace AI.

Generates empathetic, emotion-aware replies. The current implementation
uses a curated pool of hand-crafted responses per emotion with random
selection to avoid repetition across turns.

Future ML integration:
    Replace `generate_response` with a call to an LLM API
    (e.g., Gemini, GPT-4) that receives the emotion label and
    conversation history for truly dynamic, personalised replies.
"""

import random
from typing import Dict, List

# ---------------------------------------------------------------------------
# Response pools — each emotion has multiple empathetic variants
# ---------------------------------------------------------------------------

_RESPONSES: Dict[str, List[str]] = {
    "sad": [
        "I'm really sorry you're feeling this way. 💙 It's okay to feel sad — "
        "your feelings are completely valid. Would you like to talk more about what's going on?",

        "Sadness can feel so heavy. You don't have to carry it alone. "
        "I'm right here with you. What's been weighing on your heart lately?",

        "It sounds like you're going through a tough time. "
        "Please be gentle with yourself — healing takes time, and that's perfectly okay.",

        "I hear you. Sometimes things feel overwhelming and that's alright. "
        "Take it one small step at a time. I'm here if you want to share more.",
    ],
    "anxious": [
        "It sounds like you're under a lot of pressure right now. 🌿 "
        "Take a slow, deep breath with me. In… and out. "
        "Remember: you've gotten through hard moments before, and you can do it again.",

        "Anxiety can make everything feel urgent and scary. "
        "You're not alone in this. Let's slow down together — what's the biggest worry on your mind right now?",

        "Feeling stressed is your mind's way of signalling that something matters to you. "
        "That's okay. Let's try to break it down into smaller pieces — what feels most overwhelming?",

        "I'm here for you. Anxiety is tough, but so are you. "
        "Would grounding techniques or just talking it through help right now?",
    ],
    "angry": [
        "I can sense your frustration, and it's completely understandable. 🔥 "
        "Your feelings are valid. Would you like to vent, or would you prefer some calming strategies?",

        "It sounds like something really got under your skin. "
        "Sometimes expressing anger is the first step to understanding it. What happened?",

        "Anger often hides deeper feelings — hurt, disappointment, or fear. "
        "Take your time. I'm listening without judgement.",

        "You have every right to feel angry. Let it out safely here. "
        "When you're ready, we can explore what's really driving these feelings together.",
    ],
    "happy": [
        "That's wonderful to hear! 🌟 I'm so glad you're feeling good. "
        "Would you like to share what's been bringing you joy lately?",

        "Your positive energy is contagious! 😊 "
        "Celebrating the good moments is just as important as working through the hard ones.",

        "It warms my heart to hear you're doing well! "
        "What's been the highlight of your day?",
    ],
    "neutral": [
        "Thank you for sharing with me. 🌱 I'm here and fully present. "
        "Feel free to share whatever is on your mind — big or small.",

        "I appreciate you reaching out to Solace AI. "
        "How are you feeling today? I'd love to understand what's going on for you.",

        "I'm here to listen without judgement. "
        "Whatever you'd like to talk about, we can explore it together.",

        "Sometimes it helps just to put things into words. "
        "Take all the time you need — I'm not going anywhere.",
    ],
}

# Fallback for any unexpected emotion label
_FALLBACK_RESPONSE = (
    "Thank you for reaching out. 💚 I'm here to support you. "
    "Can you tell me a little more about how you're feeling right now?"
)


def generate_response(emotion: str, text: str) -> str:  # noqa: ARG001
    """
    Generate an empathetic reply based on the detected *emotion*.

    The *text* parameter is accepted for forward-compatibility with
    context-aware or ML-based response generators.

    Args:
        emotion: Emotion label returned by `detect_emotion`.
        text:    The original user message (reserved for future use).

    Returns:
        A string containing the chatbot's empathetic reply.
    """
    pool = _RESPONSES.get(emotion, [_FALLBACK_RESPONSE])
    return random.choice(pool)
