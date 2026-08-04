from app.llm.client import OllamaClient
from app.llm.generation import generate_validated
from app.llm.prompts import MCQ_PROMPT_TEMPLATE, MCQ_RETRY_SUFFIX
from app.schemas import MCQPayload


def generate_mcq(client: OllamaClient, topic: str, difficulty: str) -> MCQPayload | None:
    result = generate_validated(
        client=client,
        prompt_template=MCQ_PROMPT_TEMPLATE,
        retry_suffix=MCQ_RETRY_SUFFIX,
        payload_cls=MCQPayload,
        topic=topic,
        difficulty=difficulty,
    )
    return result  # type: ignore[return-value]


def generate_mcq_batch(
    client: OllamaClient, topic: str, difficulty: str, count: int
) -> list[MCQPayload]:
    """Generate up to `count` valid MCQs, one LLM call (with retries) per question.

    Questions that fail validation after the retry budget are skipped, not saved.
    """
    results: list[MCQPayload] = []
    for _ in range(count):
        mcq = generate_mcq(client, topic, difficulty)
        if mcq is not None:
            results.append(mcq)
    return results
