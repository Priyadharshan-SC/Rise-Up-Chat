"""
chat.py
-------
Chat route for Solace AI.

Defines the POST /chat endpoint. The request pipeline is:
    1. Validate request body via ChatRequest schema.
    2. Run safety check — if flagged, return emergency response immediately.
    3. Detect emotion from the user message.
    4. Generate an empathetic reply based on the emotion.
    5. Persist the conversation turn to the database.
    6. Return a structured ChatResponse JSON.
"""

from fastapi import APIRouter, HTTPException, status

from schemas.chat_schema import ChatRequest, ChatResponse
from services.safety import check_safety, EMERGENCY_RESPONSE
from services.emotion import detect_emotion
from services.response import generate_response
from database.db import save_conversation

# ---------------------------------------------------------------------------
# Router setup
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to Solace AI",
    description=(
        "Accepts a user message, runs safety analysis, detects emotion, "
        "and returns an empathetic AI response."
    ),
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint.

    Pipeline:
        message → safety check → emotion detection → response generation → save → respond
    """
    user_message = request.message.strip()

    # ── Step 1: Empty message guard ──────────────────────────────────────────
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message cannot be empty.",
        )

    # ── Step 2: Safety check ─────────────────────────────────────────────────
    is_safe = check_safety(user_message)

    if not is_safe:
        # Crisis detected — skip emotion detection and return emergency reply
        save_conversation(
            user_message=user_message,
            emotion="crisis",
            reply=EMERGENCY_RESPONSE,
            safe=False,
        )
        return ChatResponse(
            reply=EMERGENCY_RESPONSE,
            emotion="crisis",
            safe=False,
        )

    # ── Step 3: Emotion detection ────────────────────────────────────────────
    emotion_result = detect_emotion(user_message)
    emotion = emotion_result.get("emotion", "neutral")

    # ── Step 4: Response generation ──────────────────────────────────────────
    reply = generate_response(emotion=emotion, text=user_message)

    # ── Step 5: Persist conversation turn ────────────────────────────────────
    save_conversation(
        user_message=user_message,
        emotion=emotion,
        reply=reply,
        safe=True,
    )

    # ── Step 6: Return structured response ───────────────────────────────────
    return ChatResponse(reply=reply, emotion=emotion, safe=True)
