# SkillDrill — Functional & Flow Specification

Local-first MCQ and scenario-based practice engine for job seekers
Prepared for: Engineering handoff
Target hardware: Intel i7 desktop, NVIDIA RTX 4060 (8GB VRAM), Ubuntu
Document version: 1.0

## 1. Purpose & Scope

This document specifies a locally-run application that helps fresh job seekers practice technical topics (SQL, Python, OOP, and similar) through auto-generated multiple-choice questions (MCQs) and scenario-based questions, ranging from basic to mid difficulty. The system runs on the user's own machine using a local LLM, so it works offline after setup and requires no per-question API cost.

### 1.1 In scope
- Selecting a topic and difficulty level (basic / mid)
- Generating N multiple-choice questions for a topic, with 4 options and one correct answer
- Generating N scenario-based questions (short case + question) with a model answer or grading rubric
- Deduplicating generated questions against the existing question bank
- Serving questions to the user in a quiz interface
- Auto-grading MCQs and rubric-grading scenario answers
- Tracking per-topic performance over time to highlight weak areas
- Growing the local question bank over time via background generation

### 1.2 Out of scope for v1
- Multiplayer / competitive quizzes
- Cloud sync or multi-device accounts
- Video or audio question formats
- Advanced/senior-level or highly specialized topics (initial focus is basic–mid, broad-audience topics)

## 2. System Flow Overview

1. User selects a topic (e.g. SQL, Python, OOP) and a difficulty level.
2. If enough unused questions already exist in the local question bank for that topic/difficulty, the quiz UI serves them immediately.
3. If the bank is low, a generation job runs: the local LLM produces a batch of MCQs and scenario questions for that topic/difficulty.
4. Each new question is embedded and compared against existing questions; near-duplicates are discarded.
5. Surviving questions are validated for format (exactly one correct MCQ option, non-empty rubric for scenarios) and saved to the question bank.
6. The user takes the quiz: MCQs are graded instantly on submission; scenario answers are graded by the LLM against the stored rubric.
7. Results are shown per question (correct/incorrect + explanation) and summarized per topic.
8. Performance history accumulates per topic, surfacing weak areas for the user to re-practice.

## 3. Component Breakdown

### 3.1 Topic & difficulty selector
Simple UI step where the user picks a topic from a configurable list (SQL, Python, OOP, Data Structures, etc.) and a difficulty (basic / mid). Topics should be config-driven (a list in the database or a config file), not hardcoded, so new topics can be added without code changes.

### 3.2 Local LLM generation engine
Ollama running locally, serving a quantized open-weight model well-suited to technical content.

| Model | Quantization | Approx. VRAM | Notes |
|---|---|---|---|
| Qwen2.5 7B Instruct | Q4_K_M | ~5 GB | Strong at structured JSON + technical/coding content; recommended default |
| Llama 3.1 8B Instruct | Q4_K_M | ~5.5–6 GB | Good general-purpose alternative |
| nomic-embed-text | — | <1 GB | Embedding model, used only for deduplication |

Generation should run as a background batch job (e.g. 50–100 questions per topic/difficulty at a time), not synchronously while a user waits mid-quiz. This keeps the quiz UI instant regardless of GPU load.

### 3.3 MCQ generator
Prompts the LLM to produce, per request: a question stem, four answer options, the index of the correct option, a one-line explanation of why it's correct, and a difficulty tag. Ask for strict JSON output and validate it before saving — discard/retry any response that fails to parse or has anything other than exactly one correct option.

### 3.4 Scenario question generator
Prompts the LLM to produce a short realistic scenario (2–4 sentences) plus an open question, along with a model answer and a short rubric (2–4 key points a good answer should cover). Used later by the grading engine.

### 3.5 Deduplication & quality checker
Before a newly generated question enters the bank: embed its text with a local embedding model, compare against existing questions in the same topic via cosine similarity, and discard near-duplicates above a similarity threshold (tune empirically, e.g. ~0.9). Also run basic format validation (no empty fields, MCQ has exactly one correct answer, options aren't all identical).

### 3.6 Question bank
Local SQLite database storing every accepted question, keyed by topic and difficulty, with a flag for whether a given user has already seen it (so repeat practice sessions surface fresh material first).

### 3.7 Quiz engine / UI
Serves a quiz session of N questions (user-configurable count) for the chosen topic/difficulty, mixing MCQs and scenario questions. Reads only from the question bank — no LLM calls during the quiz itself, so navigation feels instant.

### 3.8 Grading engine
- MCQs: instant, deterministic — compare submitted option index to the stored correct index
- Scenario questions: submitted free-text answer is sent to the local LLM along with the stored rubric; the LLM returns which rubric points were covered and a short score, which is then shown to the user with the model answer for comparison

### 3.9 Performance analytics
Aggregates results per topic and difficulty over time: accuracy percentage, most-missed question types, and a simple "weak topics" view so the user knows where to focus next. All computed from the local attempts table — no external analytics service needed.

## 4. Data Model

### 4.1 Question (SQLite)

| Field | Type | Notes |
|---|---|---|
| id | integer | PK |
| topic | text | e.g. SQL, Python, OOP |
| difficulty | text | basic / mid |
| type | text | mcq / scenario |
| question_text | text | |
| options | json | MCQ only: array of 4 options |
| correct_index | integer | MCQ only |
| explanation | text | MCQ only: why the answer is correct |
| model_answer | text | scenario only |
| rubric | json | scenario only: list of key points |
| embedding | blob | for dedup checks |
| created_at | datetime | |

### 4.2 Attempt (SQLite)

| Field | Type | Notes |
|---|---|---|
| id | integer | PK |
| question_id | integer | FK |
| user_answer | text | option index or free text |
| is_correct | boolean | MCQ: exact; scenario: score ≥ threshold |
| score | real | scenario only, 0–100 |
| attempted_at | datetime | |

## 5. Suggested Technology Stack

| Layer | Suggestion |
|---|---|
| LLM runtime | Ollama (local), Qwen2.5 7B or Llama 3.1 8B, Q4_K_M quantization |
| Embeddings | nomic-embed-text via Ollama |
| Backend API | Python, FastAPI |
| Database | SQLite |
| Frontend | React (or simple server-rendered pages) served locally |
| Background jobs | APScheduler or a simple cron-triggered script for batch generation |

## 6. Non-Functional Requirements
- Offline-capable after initial model download — no internet dependency for core quiz-taking
- Quiz navigation must feel instant (questions served from local DB, not generated live)
- Generated content must be validated before being shown to a user (no malformed MCQs, no empty rubrics)
- Runs entirely on a single Ubuntu desktop; no cloud infrastructure required

## 7. Suggested Build Phases

**Phase 1 — Core generation pipeline**
- Ollama integration, MCQ generation prompt + JSON validation
- Scenario generation prompt + JSON validation
- Question bank schema + save logic

**Phase 2 — Quality & dedup**
- Embedding-based deduplication
- Format/quality validation rules

**Phase 3 — Quiz experience**
- Quiz UI: topic/difficulty selection, question flow, instant MCQ grading
- Scenario grading via LLM rubric comparison

**Phase 4 — Analytics & polish**
- Per-topic performance dashboard, weak-area highlighting
- Background/scheduled bank top-up so users rarely wait on generation
- Additional topics added via config, not code changes

## 8. Open Questions for the Engineer
- Should quiz sessions be timed, or untimed/self-paced for v1?
- Fixed topic list at launch, or an admin UI to add topics later?
- Should scenario grading show the rubric breakdown to the user, or just a score + model answer?
- Desktop app shell vs. local web app for distribution?
