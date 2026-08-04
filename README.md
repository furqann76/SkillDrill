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
cp .env.example .env   # adjust model names / DB path / APP_PIN if needed

# Backend
cd backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# Frontend
cd ../frontend
npm install
```

## Running

**Phase 1 (current)** — no server yet, just the generation pipeline. Generate and save a batch
of MCQs for one topic/difficulty directly:

```bash
cd backend
.venv/bin/python -m app.generate_cli --topic Python --difficulty basic --count 10
```

This writes validated questions straight into the SQLite bank at `backend/data/skilldrill.db`.
Anything that fails JSON/schema validation after a bounded number of retries is logged and
skipped — never saved malformed.

Once the FastAPI app and React frontend are wired up (Phase 3), full run instructions will be
added here.

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
