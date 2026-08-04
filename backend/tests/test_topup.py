import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Base, Question, Topic
from app.topup import top_up_bank, top_up_topic

VALID_MCQ_JSON = {
    "question_text": "Which keyword defines a function in Python?",
    "options": ["func", "def", "function", "lambda"],
    "correct_index": 1,
    "explanation": "'def' is the keyword used to define a function.",
    "difficulty": "basic",
}

VALID_SCENARIO_JSON = {
    "question_text": "A junior dev's script crashes with an IndexError. What do they check?",
    "model_answer": "Check bounds before indexing.",
    "rubric": ["Checks list length", "Handles the edge case"],
    "difficulty": "basic",
}


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


@pytest.fixture
def topic(session):
    t = Topic(name="python", display_name="Python", is_active=True)
    session.add(t)
    session.commit()
    return t


def make_questions(session, topic, n, difficulty="basic", qtype="mcq"):
    for _ in range(n):
        q = Question(
            topic_id=topic.id,
            difficulty=difficulty,
            type=qtype,
            question_text="existing question",
            options=["a", "b", "c", "d"] if qtype == "mcq" else None,
            correct_index=0 if qtype == "mcq" else None,
            explanation="because" if qtype == "mcq" else None,
            model_answer="answer" if qtype == "scenario" else None,
            rubric=["a", "b"] if qtype == "scenario" else None,
        )
        session.add(q)
    session.commit()


class FakeClientTyped:
    """Returns MCQ or scenario JSON depending on which prompt template is used, and a
    unique embedding each call so nothing is ever flagged as a duplicate.
    """

    def __init__(self):
        self.generate_calls = 0
        self.embed_calls = 0

    def generate_json(self, model, prompt):
        self.generate_calls += 1
        if "rubric" in prompt.lower() or "model_answer" in prompt.lower():
            return VALID_SCENARIO_JSON
        return VALID_MCQ_JSON

    def embed(self, model, text):
        # One-hot vectors are pairwise orthogonal (cosine similarity 0), so no two
        # generated questions are ever mistaken for near-duplicates in these tests.
        vector = [0.0] * 32
        vector[self.embed_calls % 32] = 1.0
        self.embed_calls += 1
        return vector


def test_top_up_topic_skips_when_bank_already_at_watermark(session, topic, monkeypatch):
    monkeypatch.setattr(settings, "generation_low_watermark", 3)
    make_questions(session, topic, 3, difficulty="basic", qtype="mcq")

    client = FakeClientTyped()
    result = top_up_topic(client, session, topic, "basic", "mcq")

    assert result is None
    assert client.generate_calls == 0


def test_top_up_topic_generates_needed_amount_when_below_watermark(session, topic, monkeypatch):
    monkeypatch.setattr(settings, "generation_low_watermark", 5)
    monkeypatch.setattr(settings, "generation_batch_size", 8)
    make_questions(session, topic, 2, difficulty="basic", qtype="mcq")  # have 2, batch target 8

    client = FakeClientTyped()
    result = top_up_topic(client, session, topic, "basic", "mcq")

    assert result is not None
    assert result.saved == 6  # 8 (batch size) - 2 (already have)


def test_top_up_bank_only_touches_active_topics(session, monkeypatch):
    monkeypatch.setattr(settings, "generation_low_watermark", 100)
    monkeypatch.setattr(settings, "generation_batch_size", 1)

    inactive = Topic(name="inactive-topic", display_name="Inactive", is_active=False)
    session.add(inactive)
    session.commit()

    client = FakeClientTyped()
    results = top_up_bank(session, client)

    assert results == []
    assert client.generate_calls == 0


def test_top_up_bank_covers_all_difficulty_and_type_combos(session, topic, monkeypatch):
    monkeypatch.setattr(settings, "generation_low_watermark", 1)
    monkeypatch.setattr(settings, "generation_batch_size", 1)

    client = FakeClientTyped()
    results = top_up_bank(session, client)

    combos = {(name, difficulty, qtype) for name, difficulty, qtype, _ in results}
    assert combos == {
        ("python", "basic", "mcq"),
        ("python", "basic", "scenario"),
        ("python", "mid", "mcq"),
        ("python", "mid", "scenario"),
    }
