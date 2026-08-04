# SkillDrill

Local-first MCQ and scenario-based technical interview practice engine. Runs entirely on your
own machine via [Ollama](https://ollama.com) — no cloud dependency, no per-question API cost.

See [`SkillDrill-Spec.md`](./SkillDrill-Spec.md) for the full functional spec.

## Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, SQLite
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
cp .env.example .env   # adjust APP_PIN, SESSION_SECRET, model names etc.
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# Frontend
cd ../frontend
npm install
```

## Running

**1. Generate some questions first** — the quiz UI only reads from the bank, it never calls the
LLM live, so there needs to be something in the bank before you can take a quiz:

```bash
cd backend
.venv/bin/python -m app.generate_cli --topic Python --difficulty basic --count 20
```

This validates, deduplicates (via embedding cosine similarity), and saves questions to
`backend/data/skilldrill.db`. Anything that fails JSON/schema validation after a bounded number
of retries, or is a near-duplicate of an existing question, is logged and skipped — never saved
malformed or repeated. Use `--type scenario` for scenario questions.

**2. Start the backend API:**

```bash
cd backend
.venv/bin/uvicorn app.main:app --reload --port 8000
```

**3. Start the frontend:**

```bash
cd frontend
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). Log in with `APP_PIN` from your
`.env`, create a profile, pick a topic/difficulty, and take the quiz.

## Development

```bash
# Backend lint/format
cd backend
.venv/bin/ruff check .
.venv/bin/black .

# Backend tests
.venv/bin/pytest
```

## Architecture notes / deviations from the spec

- **Multi-profile support**: the spec's data model (section 4) assumes a single user. Since this
  build supports multiple local profiles, the "has this question been seen" flag described in
  spec 3.6 is implemented as a `QuestionSeen(profile_id, question_id)` join table instead of a
  single boolean column on `Question`, and `Attempt` carries a `profile_id`.
- **Auth**: a single app-level PIN (`APP_PIN` in `.env`), not per-profile passwords — profiles
  separate practice history, not access.
- **Topics**: topic list lives in the `topics` DB table with an admin UI to manage it (per your
  answer to the spec's open question), rather than a static config file.
