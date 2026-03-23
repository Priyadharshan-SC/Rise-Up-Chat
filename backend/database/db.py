"""
db.py
-----
Database engine, session factory, and CRUD helpers for Solace AI.

Uses SQLite via SQLAlchemy. The DB file is created automatically at startup.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from database.models import Base, Chat, Conversation

# ---------------------------------------------------------------------------
# Engine & session
# ---------------------------------------------------------------------------

DATABASE_URL = "sqlite:///./solace.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency: yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Chat session CRUD
# ---------------------------------------------------------------------------

def create_chat(db: Session, title: str = "New Chat") -> Chat:
    chat = Chat(chat_id=str(uuid.uuid4()), title=title, created_at=datetime.utcnow())
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_all_chats(db: Session) -> List[Chat]:
    return db.query(Chat).order_by(Chat.created_at.desc()).all()


def get_chat(db: Session, chat_id: str) -> Optional[Chat]:
    return db.query(Chat).filter(Chat.chat_id == chat_id).first()


def update_chat_title(db: Session, chat_id: str, title: str) -> None:
    chat = get_chat(db, chat_id)
    if chat:
        chat.title = title[:60]   # cap title length
        db.commit()


def delete_chat(db: Session, chat_id: str) -> bool:
    chat = get_chat(db, chat_id)
    if not chat:
        return False
    db.delete(chat)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Conversation CRUD
# ---------------------------------------------------------------------------

def save_conversation(
    db: Session,
    chat_id: str,
    user_message: str,
    emotion: str,
    confidence: float,
    reply: str,
    safe: bool,
    risk_level: str = "low",
    response_source: str = "rule_based",
) -> Conversation:
    record = Conversation(
        chat_id=chat_id,
        user_message=user_message,
        emotion=emotion,
        confidence=confidence,
        reply=reply,
        safe=safe,
        risk_level=risk_level,
        response_source=response_source,
        sos_triggered=False,
        timestamp=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_recent_messages(db: Session, chat_id: str, limit: int = 2) -> List[Conversation]:
    """Fetch the last *limit* turns from a chat (for short-term memory)."""
    return (
        db.query(Conversation)
        .filter(Conversation.chat_id == chat_id)
        .order_by(Conversation.timestamp.desc())
        .limit(limit)
        .all()
    )[::-1]   # reverse so oldest-first


def get_conversations(db: Session, chat_id: str) -> List[Conversation]:
    return (
        db.query(Conversation)
        .filter(Conversation.chat_id == chat_id)
        .order_by(Conversation.timestamp.asc())
        .all()
    )


def trigger_sos(db: Session, chat_id: str) -> bool:
    """Mark the latest conversation row in the chat as SOS triggered."""
    record = (
        db.query(Conversation)
        .filter(Conversation.chat_id == chat_id)
        .order_by(Conversation.timestamp.desc())
        .first()
    )
    if not record:
        return False
    record.sos_triggered = True
    db.commit()
    return True
