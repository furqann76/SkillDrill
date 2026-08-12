from django.conf import settings

from llm.client import OllamaClient
from quizbank.models import Question, Topic
from quizbank.pipeline import (
    GenerationStats,
    generate_and_save_mcq_batch,
    generate_and_save_scenario_batch,
)

DIFFICULTIES = ("basic", "mid")
QUESTION_TYPES = ("mcq", "scenario")


def count_questions(topic_id: int, difficulty: str, qtype: str) -> int:
    return Question.objects.filter(topic_id=topic_id, difficulty=difficulty, type=qtype).count()


def top_up_topic(
    client: OllamaClient, topic: Topic, difficulty: str, qtype: str
) -> GenerationStats | None:
    """Generate more `qtype` questions for topic/difficulty if the bank is below the
    low watermark. Returns None (and generates nothing) if there's already enough.
    """
    count = count_questions(topic.id, difficulty, qtype)
    if count >= settings.GENERATION_LOW_WATERMARK:
        return None

    needed = settings.GENERATION_BATCH_SIZE - count
    generate_batch = (
        generate_and_save_mcq_batch if qtype == "mcq" else generate_and_save_scenario_batch
    )
    return generate_batch(client, topic.name, difficulty, needed)


def top_up_bank(client: OllamaClient) -> list[tuple[str, str, str, GenerationStats]]:
    """Check every active topic/difficulty/type combo and top up any that have fallen
    below the low watermark. Returns (topic_name, difficulty, type, stats) for each
    combo that actually triggered generation.
    """
    results: list[tuple[str, str, str, GenerationStats]] = []

    for topic in Topic.objects.filter(is_active=True):
        for difficulty in DIFFICULTIES:
            for qtype in QUESTION_TYPES:
                stats = top_up_topic(client, topic, difficulty, qtype)
                if stats is not None:
                    results.append((topic.name, difficulty, qtype, stats))

    return results
