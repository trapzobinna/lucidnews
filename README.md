# Lucid — AI Information Diet Aggregator

Lucid replaces infinite-scroll news feeds with a finite, credibility-scored, goal-tailored set of stories — filtering out clickbait by tactic, not topic.

## Stack
- **Backend**: FastAPI, SQLAlchemy, SQLite, apscheduler
- **AI/NLP**: SentenceTransformers (embeddings), Anthropic Claude (summarization)
- **Frontend**: React 18, Vite, TailwindCSS

## Setup & Running

### Option 1: Docker (Recommended)
1. Copy `backend/.env.example` to `backend/.env` and add your `ANTHROPIC_API_KEY`.
2. Run `docker compose up --build`.
3. Open `http://localhost:5173` for the frontend.

### Option 2: Local Dev
**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Add ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## First Run
By default, the pipeline is scheduled to run daily at 6:00 AM.
To trigger it immediately for testing:
1. Open the app (`http://localhost:5173`).
2. If it's your first time, you'll see a "No Briefing Yet" screen with a **Run Pipeline Now** button. Click it.
3. Wait 1-2 minutes (check backend logs for progress).
4. Refresh the page to see your briefing.
