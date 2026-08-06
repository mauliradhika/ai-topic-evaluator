AI-evaluated speaking/writing practice platform.

## Flow
1. User picks a topic
2. Random weighted draw gives a subtopic + curated references
3. User sets prep time (2-15 min) and response time (1-10 min)
4. User writes or speaks (Web Speech API) their response, closeable anytime
5. Claude evaluates against a rubric that's weighted by mode (speak/write)
   and strictness (lenient/moderate/strict)
6. User gets a weighted score + per-criterion breakdown + personalized feedback

## Structure
```
backend/    FastAPI + SQLAlchemy + SQLite, Claude API evaluator
frontend/   React (Vite) + react-router-dom
```

## Backend setup
```bash
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
uvicorn app.main:app --reload --port 8000
```
First run auto-creates and seeds the SQLite DB (backend/prepspeak.db) with
sample topics in app/seed_data.py — edit/extend that file to add your own.

## Frontend setup
```bash
cd frontend
npm install
npm run dev
```
If your backend isn't on localhost:8000, set VITE_API_BASE in a .env file.

## Status / what's left
- [x] Topic engine, weighted random subtopic draw, references
- [x] Session config (mode, strictness, prep/response time)
- [x] Rubric weighting engine (mode + strictness -> criteria weights)
- [x] Claude-based evaluator with structured JSON scoring
- [x] Prep timer page, response capture page (write + speak), results page
- [ ] App.jsx routing not yet wired up (SessionProvider + react-router routes
      connecting TopicSelect -> Prep -> Response -> Results) - left as the
      next implementation step
- [ ] Styling is unstyled/minimal - class names are in place (see App.css)
      but need actual CSS
- [ ] Session history, dashboard, auth - not built, future phase

## Known constraints
- Web Speech API (speak mode) only works reliably in Chrome/Edge
- Evaluator calls Claude on every submit - no retry/rate-limit handling yet