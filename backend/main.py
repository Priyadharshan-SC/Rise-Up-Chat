"""
main.py
-------
Entry point for the Solace AI FastAPI application.

Run with:
    uvicorn main:app --reload
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.chat import router as chat_router
from routes.sessions import router as sessions_router
from database.db import init_db

# ── Create all SQLite tables on startup ───────────────────────────────────────
init_db()

# ── App Factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Solace AI",
    description=(
        "An empathetic mental wellness chatbot powered by FastAPI. "
        "Solace AI detects your emotional state and responds with care, "
        "while prioritising your safety above all else."
    ),
    version="2.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(sessions_router)

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["Health"], summary="Health check")
async def health_check() -> dict:
    return {
        "status": "ok",
        "app": "Solace AI",
        "version": "2.0.0",
        "message": "Welcome to Solace AI — your mental wellness companion. 💙",
    }

# ── Serve Frontend ────────────────────────────────────────────────────────────
current_dir  = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(current_dir, "..", "frontend")

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
