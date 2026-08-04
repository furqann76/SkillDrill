import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.bank import get_or_create_topic, get_topic_embeddings, save_mcq, save_scenario
from app.config import settings
from app.dedup import is_near_duplicate
from app.llm.client import OllamaClient
from app.llm.mcq_generator import generate_mcq
from app.llm.scenario_generator import generate_scenario
from app.models import Question

logger = logging.getLogger("skilldrill.pipeline")


@dataclass
class GenerationStats:
    saved: int = 0
    skipped_invalid: int = 0
    skipped_duplicate: int = 0
    saved_questions: list[Question] = field(default_factory=list)


def generate_and_save_mcq_batch(
    client: OllamaClient, session: Session, topic_name: str, difficulty: str, count: int
) -> GenerationStats:
    """Generate up to `count` MCQs: validate, dedup against the topic's existing bank
    (including questions saved earlier in this same batch), then save.
    """
    stats = GenerationStats()
    topic = get_or_create_topic(session, topic_name)
    existing_embeddings = get_topic_embeddings(session, topic.id)

    for _ in range(count):
        payload = generate_mcq(client, topic_name, difficulty)
        if payload is None:
            stats.skipped_invalid += 1
            continue

        embedding = client.embed(settings.ollama_embedding_model, payload.question_text)

        if is_near_duplicate(embedding, existing_embeddings, settings.dedup_similarity_threshold):
            stats.skipped_duplicate += 1
            logger.info("discarded near-duplicate MCQ: %s", payload.question_text[:80])
            continue

        question = save_mcq(session, topic_name, payload, embedding=embedding)
        existing_embeddings.append(embedding)
        stats.saved += 1
        stats.saved_questions.append(question)

    return stats


def generate_and_save_scenario_batch(
    client: OllamaClient, session: Session, topic_name: str, difficulty: str, count: int
) -> GenerationStats:
    stats = GenerationStats()
    topic = get_or_create_topic(session, topic_name)
    existing_embeddings = get_topic_embeddings(session, topic.id)

    for _ in range(count):
        payload = generate_scenario(client, topic_name, difficulty)
        if payload is None:
            stats.skipped_invalid += 1
            continue

        embedding = client.embed(settings.ollama_embedding_model, payload.question_text)

        if is_near_duplicate(embedding, existing_embeddings, settings.dedup_similarity_threshold):
            stats.skipped_duplicate += 1
            logger.info("discarded near-duplicate scenario: %s", payload.question_text[:80])
            continue

        question = save_scenario(session, topic_name, payload, embedding=embedding)
        existing_embeddings.append(embedding)
        stats.saved += 1
        stats.saved_questions.append(question)

    return stats
