> ## 🚀 Also by me: [AI Job Agent](https://github.com/furqann76/JobAgent)
>
> An AI agent that finds the right jobs for you, scores each one against your real experience,
> and drafts a tailored CV and cover letter for the ones worth applying to — running on your own
> machine with a local AI model. Built around a simple routine: **~10 good applications a day
> instead of 100 weak ones.** The agent does the searching, reading and first drafts; you make
> every decision.
>
> - **Finds jobs** from ~30 company job boards (Greenhouse and Lever public APIs), filtered by
>   the titles you want — or paste any job description yourself.
> - **Understands your field** — works out your kind of work, level and core stack, and sets
>   aside jobs that only *sound* right, always showing the reason.
> - **Transparent match scores** (skills, experience, projects, education, location) plus an
>   eligibility check — deterministic code, not AI guesswork.
> - **Ranked daily shortlist**, capped at your daily goal.
> - **Tailored CVs and cover letters** grounded only in evidence from your profile (RAG with
>   FAISS) — missing skills are listed as gaps, never invented. Export to PDF or Word.
> - **CV import** (PDF, Word or text), reviewed by you before anything is saved.
> - **Application tracking** on a Kanban board, with optional browser form-filling that
>   **never submits without your explicit confirmation**.
> - **Insights, notifications and multiple accounts**, each fully separate.
>
> **Stack:** Python 3.12, Django 6, DRF, PostgreSQL, Redis, Celery, Ollama
> (`qwen2.5:7b-instruct` + `nomic-embed-text`), FAISS, Pydantic, Playwright, React 19 +
> TypeScript + Vite.
>
> 👉 **[github.com/furqann76/JobAgent](https://github.com/furqann76/JobAgent)**

---

# SkillDrill

Local-first MCQ and scenario-based technical interview practice engine. Runs entirely on your
own machine via [Ollama](https://ollama.com) — no cloud dependency, no per-question API cost.

See [`SkillDrill-Spec.md`](./SkillDrill-Spec.md) for the full functional spec.

## Stack

- **Backend**: Python 3.12, Django + Django REST Framework, SQLite
- **Frontend**: React + TypeScript (Vite)
- **LLM runtime**: Ollama — `qwen2.5:7b-instruct-q4_K_M` for generation/grading, `nomic-embed-text`
  for deduplication

## Prerequisites

- Python 3.12+
- Node 20+
- [Ollama](https://ollama.com) installed and running (`ollama serve`, or the systemd service)
- The two models pulled:
  ```
  ollama pull qwen2.5:7b-instruct-q4_K_M
  ollama pull nomic-embed-text
  ```
- An NVIDIA GPU with enough VRAM to run the 7B model is recommended but not required (Ollama
  will fall back to CPU). Verify GPU offload with `ollama ps` while a generation is running —
  it should show `100% GPU`.

## Setup

```bash
# Backend
cd backend
cp .env.example .env   # adjust SESSION_SECRET, model names etc.
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser   # for the admin panel

# Frontend
cd ../frontend
npm install
```

## Running

**1. Generate some questions first** — the quiz UI only reads from the bank, it never calls the
LLM live, so there needs to be something in the bank before you can take a quiz:

```bash
cd backend
.venv/bin/python manage.py generate_questions --topic Python --difficulty basic --count 20
```

This validates, deduplicates (via embedding cosine similarity), and saves questions to
`backend/data/skilldrill.db`. Anything that fails JSON/schema validation after a bounded number
of retries, or is a near-duplicate of an existing question, is logged and skipped — never saved
malformed or repeated. Use `--type scenario` for scenario questions.

**2. Start the backend and frontend together:**

```bash
./dev.sh
```

This runs the Django backend (`:8000`) and the Vite dev server (`:5173`) side by side and stops
both on Ctrl+C. To run them separately instead:

```bash
cd backend  && .venv/bin/python manage.py runserver 8000
cd frontend && npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). Sign up with an email, username, and
password — this creates your account and its one practice profile in the same step — then pick a
topic/difficulty and take the quiz. From the quiz setup screen you can also open **View progress**
(per-topic accuracy, weak-topic highlighting) and **Manage topics** (add topics,
activate/deactivate — an inactive topic is hidden from quiz setup).

**Admin panel**: `http://localhost:8000/admin` — log in with the superuser you created above.
Full CRUD over topics, questions, accounts/profiles, question-seen records, and attempts, with
filtering and search built in. This is the fastest way to eyeball generated content, fix a bad
question, or seed/clean up data by hand. It shares the same `auth.User` table as the app's own
login, just gated on `is_staff` — a regular signup can never log into `/admin`.

**Background bank top-up**: on startup, the backend schedules a recurring job (every
`TOP_UP_INTERVAL_MINUTES`, default 30) that checks every active topic × difficulty × question
type and generates more questions — up to `GENERATION_BATCH_SIZE` — for any combo that's fallen
below `GENERATION_LOW_WATERMARK`. It runs on a background thread, never in the request path, so
it never blocks the quiz UI. Set `TOP_UP_ENABLED=false` in `.env` to disable it.

## Development

```bash
# Backend lint/format
cd backend
.venv/bin/ruff check .
.venv/bin/black .

# Backend tests (pytest-django, isolated in-memory test DB -- never touches
# backend/data/skilldrill.db)
.venv/bin/pytest
```

## Project layout (backend)

```
backend/
  manage.py
  config/       Django project settings, root urls.py, wsgi/asgi
  quizbank/     Models, Django admin registrations, business logic
                (bank/pipeline/dedup/quiz_selection/grading/analytics/topup),
                the APScheduler wiring, and the generate_questions/import_legacy_data
                management commands
  api/          DRF serializers, views, and urls.py for the /api/* routes the
                frontend talks to
  llm/          Framework-agnostic Ollama client, prompts, and Pydantic schemas
                for validating LLM JSON output -- no Django/DRF imports here
                except reading settings, so it's easy to reason about in isolation
  tests/        pytest-django test suite
```

## Architecture notes / deviations from the spec

- **Profile support**: the spec's data model (section 4) assumes a single user. This build keeps
  `Profile` as its own model (one per account, created automatically at signup) rather than
  folding its fields into `User`, so the "has this question been seen" flag described in spec 3.6
  stays a `QuestionSeen(profile, question)` join table instead of a boolean column on `Question`,
  and `Attempt` carries a `profile`.
- **Auth**: real accounts (email + username + password, hashed via Django's `auth.User`), one
  profile per account. Session-based, via `django.contrib.auth`'s `login()`/`logout()` — not
  wired through DRF's authentication-class layer, so writes stay `csrf_exempt` the same way they
  always were under APIView, rather than needing `X-CSRFToken` plumbing on the frontend for a
  same-origin, `SameSite=Lax` local app. `quiz/*` and `analytics` derive the caller's profile from
  the session instead of trusting a client-supplied `profile_id`.
- **Topics**: topic list lives in the `Topic` model with an in-app admin UI to manage it (per
  your answer to the spec's open question) as well as full CRUD via the Django admin panel,
  rather than a static config file.
- **Backend framework**: the spec (section 5) suggested FastAPI; this was later rebuilt on
  Django + DRF specifically to get Django's admin panel for free. The API contract at `/api/*`
  is unchanged, so the frontend didn't need any changes for the switch.
