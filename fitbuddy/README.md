# FitBuddy – AI Fitness Plan Generator

FastAPI + Google Gemini + SQLite. Generates a 7-day workout plan, a nutrition tip,
revises the plan from feedback, and has a coach dashboard.

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then paste your key from https://aistudio.google.com/apikey
uvicorn app.main:app --reload   # run from the fitbuddy/ folder
```
Open http://127.0.0.1:8000 (app) and http://127.0.0.1:8000/docs (API).

## Routes
| Route | Purpose |
|---|---|
| `GET /` | Input form |
| `POST /generate-workout` | Form → Gemini Pro plan + Flash tip → saved → `result.html` |
| `POST /submit-feedback` | Form → revised plan via Gemini Pro |
| `GET /view-all-users` | Coach dashboard (original vs updated plans) |
| `POST /delete-user/{id}` | Delete a user from the dashboard |
| `POST /generate-plan`, `POST /update-plan/{id}`, `GET /nutrition-tip`, `POST /generate-workout/gemini` | JSON API |

Optional: drop a gym photo at `app/static/images/gym-bg.jpg` for the background.
