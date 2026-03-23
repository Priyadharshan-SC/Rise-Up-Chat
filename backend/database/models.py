"""
models.py
---------
SQLAlchemy ORM models for Solace AI.

Tables:
    Chat         - Represents a conversation session.
    Conversation - Represents a single turn in a chat session.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Chat(Base):
    """A chat session (like a ChatGPT conversation thread)."""
    __tablename__ = "chats"

    chat_id    = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title      = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship(
        "Conversation", back_populates="chat", cascade="all, delete-orphan"
    )


class Conversation(Base):
    """A single user↔bot turn within a chat session."""
    __tablename__ = "conversations"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    chat_id         = Column(String, ForeignKey("chats.chat_id"), nullable=False)
    user_message    = Column(Text, nullable=False)
    emotion         = Column(String, default="neutral")
    confidence      = Column(Float,  default=0.0)
    reply           = Column(Text,   nullable=False)
    safe            = Column(Boolean, default=True)
    risk_level      = Column(String,  default="low")    # low | medium | high | crisis
    response_source = Column(String,  default="rule_based")  # llm | rule_based
    sos_triggered   = Column(Boolean, default=False)
    timestamp       = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", back_populates="conversations")
