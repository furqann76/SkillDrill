from sqlalchemy.orm import Session

from app.config import settings
from app.llm.client import OllamaClient
from app.llm.scenario_grader import grade_scenario
from app.models import Attempt, Question
from app.schemas import ScenarioGradingPayload


def grade_and_save_mcq(
    session: Session, profile_id: int, question: Question, selected_index: int
) -> Attempt:
    is_correct = selected_index == question.correct_index
    attempt = Attempt(
        profile_id=profile_id,
        question_id=question.id,
        user_answer=str(selected_index),
        is_correct=is_correct,
        score=None,
    )
    session.add(attempt)
    session.commit()
    return attempt


def grade_and_save_scenario(
    client: OllamaClient,
    session: Session,
    profile_id: int,
    question: Question,
    answer_text: str,
) -> tuple[Attempt, ScenarioGradingPayload] | None:
    result = grade_scenario(client, question, answer_text)
    if result is None:
        return None

    is_correct = result.score >= settings.scenario_pass_threshold
    attempt = Attempt(
        profile_id=profile_id,
        question_id=question.id,
        user_answer=answer_text,
        is_correct=is_correct,
        score=result.score,
    )
    session.add(attempt)
    session.commit()
    return attempt, result
