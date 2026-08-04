from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import db_session, require_auth
from app.grading import grade_and_save_mcq, grade_and_save_scenario
from app.llm.client import OllamaClient
from app.models import Question, Topic
from app.quiz import select_quiz_questions

router = APIRouter(prefix="/api/quiz", tags=["quiz"], dependencies=[Depends(require_auth)])

_client = OllamaClient()


class QuizStartRequest(BaseModel):
    profile_id: int
    topic: str
    difficulty: str
    count: int = 10


class QuestionOut(BaseModel):
    id: int
    type: str
    difficulty: str
    question_text: str
    options: list[str] | None = None


class QuizStartResponse(BaseModel):
    questions: list[QuestionOut]
    requested: int
    available: int


@router.post("/start", response_model=QuizStartResponse)
def start_quiz(body: QuizStartRequest, session: Session = Depends(db_session)) -> QuizStartResponse:
    topic = session.scalar(select(Topic).where(Topic.name == body.topic))
    if topic is None:
        raise HTTPException(status_code=404, detail=f"Unknown topic: {body.topic}")

    questions = select_quiz_questions(
        session, body.profile_id, topic.id, body.difficulty, body.count
    )
    out = [
        QuestionOut(
            id=q.id,
            type=q.type,
            difficulty=q.difficulty,
            question_text=q.question_text,
            options=q.options if q.type == "mcq" else None,
        )
        for q in questions
    ]
    return QuizStartResponse(questions=out, requested=body.count, available=len(out))


class GradeMCQRequest(BaseModel):
    profile_id: int
    question_id: int
    selected_index: int


class GradeMCQResponse(BaseModel):
    is_correct: bool
    correct_index: int
    explanation: str


@router.post("/grade/mcq", response_model=GradeMCQResponse)
def grade_mcq(body: GradeMCQRequest, session: Session = Depends(db_session)) -> GradeMCQResponse:
    question = session.get(Question, body.question_id)
    if question is None or question.type != "mcq":
        raise HTTPException(status_code=404, detail="MCQ question not found")

    grade_and_save_mcq(session, body.profile_id, question, body.selected_index)
    return GradeMCQResponse(
        is_correct=body.selected_index == question.correct_index,
        correct_index=question.correct_index,
        explanation=question.explanation,
    )


class GradeScenarioRequest(BaseModel):
    profile_id: int
    question_id: int
    answer_text: str


class RubricPoint(BaseModel):
    point: str
    covered: bool


class GradeScenarioResponse(BaseModel):
    score: float
    is_correct: bool
    rubric_breakdown: list[RubricPoint]
    feedback: str
    model_answer: str


@router.post("/grade/scenario", response_model=GradeScenarioResponse)
def grade_scenario_endpoint(
    body: GradeScenarioRequest, session: Session = Depends(db_session)
) -> GradeScenarioResponse:
    question = session.get(Question, body.question_id)
    if question is None or question.type != "scenario":
        raise HTTPException(status_code=404, detail="Scenario question not found")

    outcome = grade_and_save_scenario(
        _client,
        session,
        body.profile_id,
        question,
        body.answer_text,
    )
    if outcome is None:
        raise HTTPException(
            status_code=502, detail="Grading failed after retries; please try again"
        )
    attempt, result = outcome

    breakdown = [
        RubricPoint(point=point, covered=covered)
        for point, covered in zip(question.rubric, result.covered, strict=True)
    ]
    return GradeScenarioResponse(
        score=result.score,
        is_correct=attempt.is_correct,
        rubric_breakdown=breakdown,
        feedback=result.feedback,
        model_answer=question.model_answer,
    )
