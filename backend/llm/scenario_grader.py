from llm.client import OllamaClient
from llm.generation import generate_validated
from llm.prompts import GRADING_PROMPT_TEMPLATE, GRADING_RETRY_SUFFIX
from llm.schemas import ScenarioGradingPayload
from quizbank.models import Question


def grade_scenario(
    client: OllamaClient, question: Question, user_answer: str
) -> ScenarioGradingPayload | None:
    rubric = question.rubric or []

    def covered_length_matches_rubric(payload: ScenarioGradingPayload) -> str | None:
        if len(payload.covered) != len(rubric):
            return f"'covered' must have exactly {len(rubric)} items to match the rubric"
        return None

    result = generate_validated(
        client=client,
        prompt_template=GRADING_PROMPT_TEMPLATE,
        retry_suffix=GRADING_RETRY_SUFFIX,
        payload_cls=ScenarioGradingPayload,
        question_text=question.question_text,
        rubric_text="\n".join(f"- {point}" for point in rubric),
        user_answer=user_answer,
        rubric_count=len(rubric),
        log_context=f"scenario grading question_id={question.id}",
        extra_validate=covered_length_matches_rubric,
    )
    return result  # type: ignore[return-value]
