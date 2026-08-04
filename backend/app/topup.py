from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.llm.client import OllamaClient
from app.models import Question, Topic
from app.pipeline import (
    GenerationStats,
    generate_and_save_mcq_batch,
    generate_and_save_scenario_batch,
)

DIFFICULTIES = ("basic", "mid")
QUESTION_TYPES = ("mcq", "scenario")


def count_questions(session: Session, topic_id: int, difficulty: str, qtype: str) -> int:
    return session.scalar(
        select(func.count(Question.id)).where(
            Question.topic_id == topic_id,
            Question.difficulty == difficulty,
            Question.type == qtype,
        )
    )


def top_up_topic(
    client: OllamaClient, session: Session, topic: Topic, difficulty: str, qtype: str
) -> GenerationStats | None:
    """Generate more `qtype` questions for topic/difficulty if the bank is below the
    low watermark. Returns None (and generates nothing) if there's already enough.
    """
    count = count_questions(session, topic.id, difficulty, qtype)
    if count >= settings.generation_low_watermark:
        return None

    needed = settings.generation_batch_size - count
    generate_batch = (
        generate_and_save_mcq_batch if qtype == "mcq" else generate_and_save_scenario_batch
    )
    return generate_batch(client, session, topic.name, difficulty, needed)


def top_up_bank(
    session: Session, client: OllamaClient
) -> list[tuple[str, str, str, GenerationStats]]:
    """Check every active topic/difficulty/type combo and top up any that have fallen
    below the low watermark. Returns (topic_name, difficulty, type, stats) for each
    combo that actually triggered generation.
    """
    results: list[tuple[str, str, str, GenerationStats]] = []
    topics = session.scalars(select(Topic).where(Topic.is_active.is_(True))).all()

    for topic in topics:
        for difficulty in DIFFICULTIES:
            for qtype in QUESTION_TYPES:
                stats = top_up_topic(client, session, topic, difficulty, qtype)
                if stats is not None:
                    results.append((topic.name, difficulty, qtype, stats))

    return results
