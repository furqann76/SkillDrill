import pytest

from quizbank.pipeline import generate_and_save_mcq_batch

pytestmark = pytest.mark.django_db

VALID_MCQ_JSON = {
    "question_text": "Which keyword defines a function in Python?",
    "options": ["func", "def", "function", "lambda"],
    "correct_index": 1,
    "explanation": "'def' is the keyword used to define a function.",
    "difficulty": "basic",
}

DIFFERENT_MCQ_JSON = {
    "question_text": "Which data structure uses FIFO ordering?",
    "options": ["stack", "queue", "tree", "heap"],
    "correct_index": 1,
    "explanation": "A queue is First-In-First-Out.",
    "difficulty": "basic",
}


class FakeClient:
    """Scripted JSON generations paired with scripted embeddings, consumed in order."""

    def __init__(self, generations, embeddings):
        self.generations = list(generations)
        self.embeddings = list(embeddings)
        self.gen_calls = 0
        self.embed_calls = 0

    def generate_json(self, model, prompt):
        response = self.generations[self.gen_calls]
        self.gen_calls += 1
        return response

    def embed(self, model, text):
        embedding = self.embeddings[self.embed_calls]
        self.embed_calls += 1
        return embedding


def test_duplicate_within_batch_is_discarded():
    # Same question generated twice with near-identical embeddings -> second is a duplicate.
    client = FakeClient(
        generations=[VALID_MCQ_JSON, VALID_MCQ_JSON],
        embeddings=[[1.0, 0.0], [0.99, 0.05]],
    )
    stats = generate_and_save_mcq_batch(client, "Python", "basic", count=2)

    assert stats.saved == 1
    assert stats.skipped_duplicate == 1
    assert stats.skipped_invalid == 0


def test_distinct_questions_both_saved():
    client = FakeClient(
        generations=[VALID_MCQ_JSON, DIFFERENT_MCQ_JSON],
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
    )
    stats = generate_and_save_mcq_batch(client, "Python", "basic", count=2)

    assert stats.saved == 2
    assert stats.skipped_duplicate == 0


def test_dedups_against_previously_saved_questions_not_just_current_batch():
    # First batch saves one question.
    client1 = FakeClient(generations=[VALID_MCQ_JSON], embeddings=[[1.0, 0.0]])
    generate_and_save_mcq_batch(client1, "Python", "basic", count=1)

    # Second, separate batch call generates a near-duplicate of what's already in the bank.
    client2 = FakeClient(generations=[VALID_MCQ_JSON], embeddings=[[0.99, 0.05]])
    stats2 = generate_and_save_mcq_batch(client2, "Python", "basic", count=1)

    assert stats2.saved == 0
    assert stats2.skipped_duplicate == 1
