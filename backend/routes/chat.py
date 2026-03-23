"""
chat.py
-------
Chat route for Solace AI.

Request pipeline:
    1. Validate request body.
    2. Resolve or create a chat session.
    3. Safety check → if crisis, return emergency response immediately.
    4. Detect emotion.
    5. Classify risk level.
    6. Smart routing: LLM (distress + confidence > 0.7 or help intent) else rule-based.
    7. Persist conversation turn.
    8. Return structured response.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from schemas.chat_schema import ChatRequest, ChatResponse
from services.safety import check_safety, EMERGENCY_RESPONSE
from services.emotion import detect_emotion
from services.response import generate_response, check_help_intent
from services.llm import generate_llm_response
from services.risk import classify_risk
from database.db import (
    get_db, create_chat, get_chat, update_chat_title,
    save_conversation, get_recent_messages,
)

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/chat", tags=["Chat"])
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to Solace AI",
)
async def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message cannot be empty.",
        )

    # ── Resolve / create chat session ─────────────────────────────────────────
    if request.chat_id:
        session = get_chat(db, request.chat_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found.")
    else:
        # Auto-create a new session; title = first 50 chars of message
        title = user_message[:50] + ("…" if len(user_message) > 50 else "")
        session = create_chat(db, title=title)

    chat_id = session.chat_id

    # Update title from first real message if still default
    if session.title == "New Chat":
        update_chat_title(db, chat_id, user_message[:50])

    # ── Safety check ──────────────────────────────────────────────────────────
    is_safe = check_safety(user_message)

    if not is_safe:
        save_conversation(
            db=db, chat_id=chat_id, user_message=user_message,
            emotion="crisis", confidence=1.0,
            reply=EMERGENCY_RESPONSE, safe=False,
            risk_level="crisis", response_source="rule_based",
        )
        return ChatResponse(
            reply=EMERGENCY_RESPONSE, emotion="crisis",
            safe=False, risk_level="crisis",
            response_source="rule_based", chat_id=chat_id,
        )

    # ── Emotion detection ─────────────────────────────────────────────────────
    emotion_result = detect_emotion(user_message)
    emotion        = emotion_result.get("emotion", "neutral")
    confidence     = emotion_result.get("confidence", 0.0)

    # ── Risk level ────────────────────────────────────────────────────────────
    risk_level = classify_risk(user_message, emotion, confidence, is_safe)

    # ── Short-term memory (last 2 turns) ──────────────────────────────────────
    recent_rows = get_recent_messages(db, chat_id, limit=2)
    context = [
        {"user": row.user_message, "bot": row.reply}
        for row in recent_rows
    ]

    # ── Smart routing: LLM vs Rule-Based ─────────────────────────────────────
    wants_help      = check_help_intent(user_message)
    use_llm         = (emotion in ("sad", "anxious") and confidence > 0.7) or wants_help
    reply           = None
    response_source = "rule_based"

    if use_llm:
        print(f"[INFO] Routing to LLM  (emotion={emotion}, conf={confidence:.2f}, help={wants_help})")
        reply = generate_llm_response(emotion=emotion, text=user_message, context=context)
        if reply:
            response_source = "llm"

    if not reply:
        print(f"[INFO] Routing to Rule-Based (emotion={emotion})")
        reply = generate_response(emotion=emotion, text=user_message)
        response_source = "rule_based"

    # ── Persist ───────────────────────────────────────────────────────────────
    save_conversation(
        db=db, chat_id=chat_id, user_message=user_message,
        emotion=emotion, confidence=confidence,
        reply=reply, safe=True,
        risk_level=risk_level, response_source=response_source,
    )

    return ChatResponse(
        reply=reply, emotion=emotion, safe=True,
        risk_level=risk_level, response_source=response_source,
        chat_id=chat_id,
    )
