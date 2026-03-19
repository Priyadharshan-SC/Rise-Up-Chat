"""
db.py
-----
Database stub for Solace AI.

Currently uses an in-memory list to store conversation history.
This module is structured to be easily replaced with a real database
(e.g., PostgreSQL via SQLAlchemy, or MongoDB via Motor) in the future.

Future ML integration: conversation history can be fed into an ML model
for context-aware, personalised responses.
"""

from datetime import datetime
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# In-memory conversation store (replace with DB adapter in production)
# ---------------------------------------------------------------------------

_conversation_log: List[Dict[str, Any]] = []


def save_conversation(user_message: str, emotion: str, reply: str, safe: bool) -> Dict[str, Any]:
    """
    Persist a conversation turn to the in-memory store.

    Args:
        user_message: The original message sent by the user.
        emotion:      The detected emotion label.
        reply:        The chatbot's response.
        safe:         Whether the message passed the safety check.

    Returns:
        The saved record as a dictionary.
    """
    record = {
        "id": len(_conversation_log) + 1,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_message": user_message,
        "emotion": emotion,
        "reply": reply,
        "safe": safe,
    }
    _conversation_log.append(record)
    return record


def get_all_conversations() -> List[Dict[str, Any]]:
    """
    Retrieve all stored conversation records.

    Returns:
        A list of conversation record dictionaries.
    """
    return list(_conversation_log)


def clear_conversations() -> None:
    """Clear all conversation history (useful for testing)."""
    global _conversation_log
    _conversation_log = []
