# Solace AI – Mental Wellness Chatbot

## Overview
Solace AI is a privacy‑first, locally‑hosted mental‑wellness chatbot built with **FastAPI** (backend) and **vanilla HTML/CSS/JS** (frontend). It provides:
- Multi‑chat session management (SQLite)
- 4‑tier risk classification (low, medium, high, crisis)
- Smart routing to a fine‑tuned local LLM (Ollama llama3) with short‑term memory
- Crisis‑alert panel with helpline buttons and SOS logging
- Empathetic, context‑aware responses

The entire stack runs locally, keeping user data on‑device only.

## Project Structure
```
SolaceAI/
├─ backend/                # FastAPI server
│   ├─ database/           # SQLAlchemy models & DB utils
│   ├─ routes/             # API endpoints (chat, sessions, SOS)
│   ├─ services/           # Safety, emotion, risk, LLM, response
│   ├─ main.py             # App entry point
│   ├─ build_custom_model.py
│   └─ requirements.txt    # Python dependencies
├─ frontend/               # Static assets served by FastAPI
│   ├─ index.html
│   ├─ script.js
│   └─ style.css
├─ .gitignore              # Files to ignore in Git
├─ README.md               # This file
└─ .env.example            # Example environment variables
```

## Setup & Installation
1. **Clone the repo** (once pushed) and `cd` into the project root.
2. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv venv
   source venv/Scripts/activate   # Windows
   pip install -r backend/requirements.txt
   ```
3. **Start Ollama** and ensure the custom model `solace-llama3` exists:
   ```bash
   ollama serve
   # In another terminal, if needed:
   ollama run solace-llama3
   ```
4. **Run the FastAPI server**:
   ```bash
   uvicorn backend.main:app --reload
   ```
5. Open a browser at `http://127.0.0.1:8000` – the frontend is served automatically.

## Development Tips
- **Hot‑reload**: `uvicorn --reload` watches for changes in `backend/`.
- **Frontend changes**: edit files under `frontend/`; the server will serve the updated assets.
- **Database migrations**: currently SQLite is used; the `init_db()` call creates tables on first run.
- **Environment variables** (optional): copy `.env.example` to `.env` and set `DATABASE_URL`, `OLLAMA_MODEL`, etc.

## Testing the Safety & Risk System
```bash
python - <<'PY'
from services.safety import check_safety
from services.risk import classify_risk

samples = [
    "I am gonna join her",
    "I feel happy today",
    "I can't take this anymore",
]
for s in samples:
    safe = check_safety(s)
    risk = classify_risk(s, 'neutral', 0.9, safe)
    print(s, "=>", "SAFE" if safe else "CRISIS", "risk", risk)
PY
```
You should see the grief‑related phrase flagged as **CRISIS**.

## Pushing to Git
```bash
git init
git add .
git commit -m "Initial commit – Solace AI with multi‑chat, risk levels, and safety fixes"
# Add remote if you have a GitHub repo
git remote add origin <your-repo-url>
git push -u origin master
```

---
*All files are now organized for a clean Git history and easy onboarding.*
