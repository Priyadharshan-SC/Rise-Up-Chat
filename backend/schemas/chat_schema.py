"""
chat_schema.py
--------------
Pydantic schemas for validating request and response bodies.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema for incoming user message."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's message to the chatbot.",
        example="I've been feeling really sad lately.",
    )
    chat_id: Optional[str] = Field(
        None,
        description="Existing session ID. If omitted, a new session is created.",
    )


class ChatResponse(BaseModel):
    """Schema for the structured chatbot response."""
    reply:           str
    emotion:         str
    safe:            bool
    risk_level:      str   = Field(..., description="low | medium | high | crisis")
    response_source: str   = Field(..., description="llm | rule_based")
    chat_id:         str   = Field(..., description="The active chat session ID.")


class ChatSessionOut(BaseModel):
    """Schema for a chat session summary (used in GET /chats)."""
    chat_id:    str
    title:      str
    created_at: str    # ISO-8601 string

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    """Schema for a single conversation turn (used in GET /chats/{id})."""
    id:              int
    user_message:    str
    emotion:         str
    confidence:      float
    reply:           str
    safe:            bool
    risk_level:      str
    response_source: str
    sos_triggered:   bool
    timestamp:       str   # ISO-8601 string

    class Config:
        from_attributes = True
