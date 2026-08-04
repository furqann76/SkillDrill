from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Question, Topic
from app.schemas import MCQPayload, ScenarioPayload


def get_or_create_topic(session: Session, name: str) -> Topic:
    topic = session.scalar(select(Topic).where(Topic.name == name))
    if topic is None:
        topic = Topic(name=name, display_name=name)
        session.add(topic)
        session.flush()
    return topic


def save_mcq(session: Session, topic_name: str, payload: MCQPayload) -> Question:
    topic = get_or_create_topic(session, topic_name)
    question = Question(
        topic_id=topic.id,
        difficulty=payload.difficulty,
        type="mcq",
        question_text=payload.question_text,
        options=payload.options,
        correct_index=payload.correct_index,
        explanation=payload.explanation,
    )
    session.add(question)
    session.commit()
    return question


def save_scenario(session: Session, topic_name: str, payload: ScenarioPayload) -> Question:
    topic = get_or_create_topic(session, topic_name)
    question = Question(
        topic_id=topic.id,
        difficulty=payload.difficulty,
        type="scenario",
        question_text=payload.question_text,
        model_answer=payload.model_answer,
        rubric=payload.rubric,
    )
    session.add(question)
    session.commit()
    return question
