import pytest
from django.conf import settings

from quizbank.models import Topic
from quizbank.topup import top_up_bank, top_up_topic

pytestmark = pytest.mark.django_db

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
def topic():
    return Topic.objects.create(name="python", display_name="Python", is_active=True)


def make_questions(topic, n, difficulty="basic", qtype="mcq"):
    from quizbank.models import Question

    for _ in range(n):
        Question.objects.create(
            topic=topic,
            difficulty=difficulty,
            type=qtype,
            question_text="existing question",
            options=["a", "b", "c", "d"] if qtype == "mcq" else None,
            correct_index=0 if qtype == "mcq" else None,
            explanation="because" if qtype == "mcq" else None,
            model_answer="answer" if qtype == "scenario" else None,
            rubric=["a", "b"] if qtype == "scenario" else None,
        )


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


def test_top_up_topic_skips_when_bank_already_at_watermark(topic, monkeypatch):
    monkeypatch.setattr(settings, "GENERATION_LOW_WATERMARK", 3)
    make_questions(topic, 3, difficulty="basic", qtype="mcq")

    client = FakeClientTyped()
    result = top_up_topic(client, topic, "basic", "mcq")

    assert result is None
    assert client.generate_calls == 0


def test_top_up_topic_generates_needed_amount_when_below_watermark(topic, monkeypatch):
    monkeypatch.setattr(settings, "GENERATION_LOW_WATERMARK", 5)
    monkeypatch.setattr(settings, "GENERATION_BATCH_SIZE", 8)
    make_questions(topic, 2, difficulty="basic", qtype="mcq")  # have 2, batch target 8

    client = FakeClientTyped()
    result = top_up_topic(client, topic, "basic", "mcq")

    assert result is not None
    assert result.saved == 6  # 8 (batch size) - 2 (already have)


def test_top_up_bank_only_touches_active_topics(monkeypatch):
    monkeypatch.setattr(settings, "GENERATION_LOW_WATERMARK", 100)
    monkeypatch.setattr(settings, "GENERATION_BATCH_SIZE", 1)

    Topic.objects.create(name="inactive-topic", display_name="Inactive", is_active=False)

    client = FakeClientTyped()
    results = top_up_bank(client)

    assert results == []
    assert client.generate_calls == 0


def test_top_up_bank_covers_all_difficulty_and_type_combos(topic, monkeypatch):
    monkeypatch.setattr(settings, "GENERATION_LOW_WATERMARK", 1)
    monkeypatch.setattr(settings, "GENERATION_BATCH_SIZE", 1)

    client = FakeClientTyped()
    results = top_up_bank(client)

    combos = {(name, difficulty, qtype) for name, difficulty, qtype, _ in results}
    assert combos == {
        ("python", "basic", "mcq"),
        ("python", "basic", "scenario"),
        ("python", "mid", "mcq"),
        ("python", "mid", "scenario"),
    }
