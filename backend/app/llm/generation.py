import logging

from pydantic import BaseModel, ValidationError

from app.config import settings
from app.llm.client import OllamaClient, OllamaError

logger = logging.getLogger("skilldrill.generation")


def generate_validated(
    *,
    client: OllamaClient,
    prompt_template: str,
    retry_suffix: str,
    payload_cls: type[BaseModel],
    topic: str,
    difficulty: str,
    max_retries: int | None = None,
) -> BaseModel | None:
    """Call the LLM, validate the JSON response against payload_cls, retry on failure.

    Returns the validated payload, or None if it still fails after max_retries
    (the caller is responsible for logging-and-skipping, never saving malformed data).
    """
    max_retries = max_retries if max_retries is not None else settings.generation_max_retries
    prompt = prompt_template.format(topic=topic, difficulty=difficulty)
    last_error: str = ""

    for attempt in range(1, max_retries + 1):
        full_prompt = prompt + (retry_suffix.format(error=last_error) if last_error else "")
        try:
            raw = client.generate_json(settings.ollama_generation_model, full_prompt)
        except OllamaError as exc:
            last_error = str(exc)
            logger.warning(
                "generation attempt %d/%d failed (transport): %s", attempt, max_retries, exc
            )
            continue

        try:
            return payload_cls.model_validate(raw)
        except ValidationError as exc:
            last_error = str(exc)
            logger.warning(
                "generation attempt %d/%d failed (validation) for topic=%s difficulty=%s: %s",
                attempt,
                max_retries,
                topic,
                difficulty,
                exc,
            )

    logger.error(
        "giving up on topic=%s difficulty=%s after %d attempts, last_error=%s",
        topic,
        difficulty,
        max_retries,
        last_error,
    )
    return None
