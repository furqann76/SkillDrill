from django.conf import settings

from llm.client import OllamaClient
from llm.scenario_grader import grade_scenario
from llm.schemas import ScenarioGradingPayload
from quizbank.models import Attempt, Question


def grade_and_save_mcq(profile_id: int, question: Question, selected_index: int) -> Attempt:
    is_correct = selected_index == question.correct_index
    return Attempt.objects.create(
        profile_id=profile_id,
        question=question,
        user_answer=str(selected_index),
        is_correct=is_correct,
        score=None,
    )


def grade_and_save_scenario(
    client: OllamaClient,
    profile_id: int,
    question: Question,
    answer_text: str,
) -> tuple[Attempt, ScenarioGradingPayload] | None:
    result = grade_scenario(client, question, answer_text)
    if result is None:
        return None

    is_correct = result.score >= settings.SCENARIO_PASS_THRESHOLD
    attempt = Attempt.objects.create(
        profile_id=profile_id,
        question=question,
        user_answer=answer_text,
        is_correct=is_correct,
        score=result.score,
    )
    return attempt, result
