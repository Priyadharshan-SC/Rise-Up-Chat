"""
sessions.py
-----------
Routes for managing Solace AI chat sessions.

Endpoints:
    GET    /chats              - list all sessions
    POST   /chats              - create a new session
    GET    /chats/{chat_id}    - get session history
    DELETE /chats/{chat_id}    - delete session + conversations
    POST   /sos                - trigger SOS on the latest turn
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from schemas.chat_schema import ChatSessionOut, ConversationOut
from database.db import (
    get_db, get_all_chats, get_chat, create_chat,
    delete_chat, get_conversations, trigger_sos,
)

router = APIRouter(prefix="/chats", tags=["Sessions"])


# ── List all sessions ─────────────────────────────────────────────────────────
@router.get("/", response_model=List[ChatSessionOut])
def list_chats(db: Session = Depends(get_db)):
    chats = get_all_chats(db)
    return [
        ChatSessionOut(
            chat_id=c.chat_id,
            title=c.title,
            created_at=c.created_at.isoformat(),
        )
        for c in chats
    ]


# ── Create a new session ──────────────────────────────────────────────────────
@router.post("/", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def new_chat(db: Session = Depends(get_db)):
    chat = create_chat(db, title="New Chat")
    return ChatSessionOut(
        chat_id=chat.chat_id,
        title=chat.title,
        created_at=chat.created_at.isoformat(),
    )


# ── Get conversation history ──────────────────────────────────────────────────
@router.get("/{chat_id}", response_model=List[ConversationOut])
def get_chat_history(chat_id: str, db: Session = Depends(get_db)):
    session = get_chat(db, chat_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    convos = get_conversations(db, chat_id)
    return [
        ConversationOut(
            id=c.id,
            user_message=c.user_message,
            emotion=c.emotion,
            confidence=c.confidence,
            reply=c.reply,
            safe=c.safe,
            risk_level=c.risk_level,
            response_source=c.response_source,
            sos_triggered=c.sos_triggered,
            timestamp=c.timestamp.isoformat(),
        )
        for c in convos
    ]


# ── Delete a session ──────────────────────────────────────────────────────────
@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_chat(chat_id: str, db: Session = Depends(get_db)):
    if not delete_chat(db, chat_id):
        raise HTTPException(status_code=404, detail="Chat session not found.")


# ── SOS trigger ───────────────────────────────────────────────────────────────
@router.post("/sos", status_code=status.HTTP_200_OK)
def sos(chat_id: str, db: Session = Depends(get_db)):
    """
    User-triggered SOS: marks the last conversation row in the session.
    Does NOT send any external alerts — user must initiate all contact.
    """
    success = trigger_sos(db, chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="No conversation found for this chat.")
    return {"status": "sos_logged", "chat_id": chat_id}
