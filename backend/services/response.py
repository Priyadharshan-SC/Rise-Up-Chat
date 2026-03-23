"""
response.py
-----------
Response generation service for Solace AI.

Generates empathetic, emotion-aware, and context-aware replies using
dynamic template combination and randomized choices to ensure human-like
and non-repetitive conversational variation.
"""

import random

# ---------------------------------------------------------------------------
# Keywords for Context and Intent Detection
# ---------------------------------------------------------------------------
ACADEMIC_KEYWORDS = ["exam", "test", "marks", "failed", "result", "study", "grade", "school", "assignment"]
RELATIONSHIP_KEYWORDS = ["love", "relationship", "breakup", "partner", "boyfriend", "girlfriend", "husband", "wife", "dating"]
WORK_KEYWORDS = ["job", "work", "boss", "office", "manager", "career", "coworker", "colleague"]
HELP_KEYWORDS = ["help", "what should i do", "how to", "get out", "advice", "stuck"]

# ---------------------------------------------------------------------------
# Response Components
# ---------------------------------------------------------------------------
OPENERS = {
    "sad": [
        "I'm so sorry you're feeling this way.", 
        "I hear you, and it sounds really heavy right now.", 
        "Sending you a gentle hug. Things seem really tough."
    ],
    "anxious": [
        "Take a slow, deep breath with me.", 
        "It sounds like you have so much on your mind.", 
        "I can feel how overwhelmed you are right now."
    ],
    "angry": [
        "It is completely understandable that you are frustrated.", 
        "I can sense how upset you are about this.", 
        "You have every right to feel angry right now."
    ],
    "happy": [
        "That's wonderful to hear!", 
        "Your positive energy is contagious!", 
        "I love hearing that things are going well!"
    ],
    "neutral": [
        "Thank you for sharing that with me.", 
        "I'm listening and I'm here for you.", 
        "I appreciate you opening up about this."
    ]
}

VALIDATIONS = {
    "sad": [
        "It's okay to feel sad—your feelings are completely valid.", 
        "Sadness can feel overwhelming, and you don't have to carry it alone.", 
        "Please be gentle with yourself right now."
    ],
    "anxious": [
        "Anxiety can make everything feel urgent and scary, but you are not alone.", 
        "Feeling stressed is your mind's way of signalling that something matters to you.", 
        "You've gotten through hard moments before, and you can do it again."
    ],
    "angry": [
        "Sometimes expressing anger is the first step to understanding it.", 
        "Anger often hides deeper feelings, and it's okay to let it out safely.", 
        "Your frustration makes total sense."
    ],
    "happy": [
        "Celebrating the good moments is just as important as working through the hard ones.", 
        "It warms my heart to hear you're doing so well.", 
        "It's so great to be able to cherish these joyful moments."
    ],
    "neutral": [
        "Sometimes it helps just to put things into words.", 
        "I'm here to listen without judgment.", 
        "Whatever you'd like to talk about, we can explore it together."
    ]
}

CONTEXT_LINES = {
    "academic": [
        "Academic struggles can be tough, but they don't define your ability or your future. You can learn from this and improve next time.",
        "School can put an unimaginable amount of pressure on you, remember to take care of yourself first.",
        "Exams and grades can be so stressful. It's important to recognize your hard work regardless of the outcome."
    ],
    "relationship": [
        "Relationships are complex and can bring up a lot of intense emotions.",
        "Navigating connection with others is rarely easy, and it takes time to process.",
        "Heartbreak and relational stress can be deeply painful. Give yourself space to heal."
    ],
    "work": [
        "Workplace stress can really take a toll on your overall well-being.",
        "Balancing career demands is challenging, and it makes sense that it's affecting you.",
        "Navigating office dynamics and job pressures is exhausting, please remember to disconnect when you can."
    ]
}

SUGGESTIONS = [
    "Could it help to break things down into smaller, more manageable steps?",
    "Sometimes talking to a trusted friend or writing your thoughts in a journal can clear your mind.",
    "Would it be helpful to take a small step back and focus on some self-care today?",
    "Perhaps focusing on just getting through today is enough of a goal for now."
]

CLOSERS = [
    "Would you like to talk more about what's going on?",
    "I'm right here with you. What feels like the hardest part right now?",
    "Take all the time you need. I'm listening.",
    "How can I best support you through this?"
]

FALLBACK_RESPONSE = "I'm here to listen. Would you like to share more about what's going on?"

def check_context(text: str) -> str:
    """Returns the primary context matched, or None if no match is found."""
    text_lower = text.lower()
    
    is_academic = any(word in text_lower for word in ACADEMIC_KEYWORDS)
    if is_academic: return "academic"
    
    is_relationship = any(word in text_lower for word in RELATIONSHIP_KEYWORDS)
    if is_relationship: return "relationship"
    
    is_work = any(word in text_lower for word in WORK_KEYWORDS)
    if is_work: return "work"
    
    return None

def check_help_intent(text: str) -> bool:
    text_lower = text.lower()
    return any(word in text_lower for word in HELP_KEYWORDS)

def generate_response(emotion: str, text: str) -> str:
    """
    Generate an empathetic reply dynamically based on detected emotion, 
    situational context, and user intent.
    """
    # Defensive programming: ensure emotion is standard
    if emotion not in OPENERS:
        emotion = "neutral"
        
    context = check_context(text)
    wants_help = check_help_intent(text)
    
    components = []
    
    # 1. Opener
    components.append(random.choice(OPENERS[emotion]))
    
    # 2. Validation
    components.append(random.choice(VALIDATIONS[emotion]))
    
    # 3. Context-aware line
    if context:
        components.append(random.choice(CONTEXT_LINES[context]))
        
    # 4. Suggestion (if help intent and distressing emotion)
    if wants_help and emotion in ["sad", "anxious", "angry"]:
        components.append(random.choice(SUGGESTIONS))
        
    # 5. Closer
    if emotion == "happy":
        components.append("What's been the highlight for you?")
    else:
        components.append(random.choice(CLOSERS))
        
    reply = " ".join(components)
    
    if not reply.strip():
        return FALLBACK_RESPONSE
        
    return reply
