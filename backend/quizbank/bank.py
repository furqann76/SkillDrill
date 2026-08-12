from llm.schemas import MCQPayload, ScenarioPayload
from quizbank.models import Question, Topic


def get_or_create_topic(name: str) -> Topic:
    topic, _ = Topic.objects.get_or_create(name=name, defaults={"display_name": name})
    return topic


def get_topic_embeddings(topic_id: int) -> list[list[float]]:
    """All stored embeddings for a topic's existing questions, for dedup comparison."""
    return list(
        Question.objects.filter(topic_id=topic_id)
        .exclude(embedding__isnull=True)
        .values_list("embedding", flat=True)
    )


def save_mcq(
    topic_name: str, payload: MCQPayload, embedding: list[float] | None = None
) -> Question:
    topic = get_or_create_topic(topic_name)
    return Question.objects.create(
        topic=topic,
        difficulty=payload.difficulty,
        type=Question.MCQ,
        question_text=payload.question_text,
        options=payload.options,
        correct_index=payload.correct_index,
        explanation=payload.explanation,
        embedding=embedding,
    )


def save_scenario(
    topic_name: str, payload: ScenarioPayload, embedding: list[float] | None = None
) -> Question:
    topic = get_or_create_topic(topic_name)
    return Question.objects.create(
        topic=topic,
        difficulty=payload.difficulty,
        type=Question.SCENARIO,
        question_text=payload.question_text,
        model_answer=payload.model_answer,
        rubric=payload.rubric,
        embedding=embedding,
    )
