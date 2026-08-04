import logging
from collections.abc import Callable

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
    max_retries: int | None = None,
    log_context: str = "",
    extra_validate: Callable[[BaseModel], str | None] | None = None,
    **format_kwargs,
) -> BaseModel | None:
    """Call the LLM, validate the JSON response against payload_cls, retry on failure.

    `format_kwargs` are interpolated into `prompt_template`. `extra_validate`, if given,
    receives the parsed payload and returns an error string to trigger a retry, or None
    if the payload is acceptable (used for checks pydantic alone can't express, e.g. a
    list length that depends on runtime data).

    Returns the validated payload, or None if it still fails after max_retries
    (the caller is responsible for logging-and-skipping, never saving malformed data).
    """
    max_retries = max_retries if max_retries is not None else settings.generation_max_retries
    prompt = prompt_template.format(**format_kwargs)
    last_error: str = ""

    for attempt in range(1, max_retries + 1):
        full_prompt = prompt + (retry_suffix.format(error=last_error) if last_error else "")
        try:
            raw = client.generate_json(settings.ollama_generation_model, full_prompt)
        except OllamaError as exc:
            last_error = str(exc)
            logger.warning(
                "generation attempt %d/%d failed (transport) %s: %s",
                attempt,
                max_retries,
                log_context,
                exc,
            )
            continue

        try:
            payload = payload_cls.model_validate(raw)
        except ValidationError as exc:
            last_error = str(exc)
            logger.warning(
                "generation attempt %d/%d failed (validation) %s: %s",
                attempt,
                max_retries,
                log_context,
                exc,
            )
            continue

        if extra_validate is not None:
            error = extra_validate(payload)
            if error is not None:
                last_error = error
                logger.warning(
                    "generation attempt %d/%d failed (post-check) %s: %s",
                    attempt,
                    max_retries,
                    log_context,
                    error,
                )
                continue

        return payload

    logger.error(
        "giving up %s after %d attempts, last_error=%s", log_context, max_retries, last_error
    )
    return None
