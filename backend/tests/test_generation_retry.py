from llm.generation import generate_validated
from llm.schemas import MCQPayload

VALID_MCQ_JSON = {
    "question_text": "Which keyword defines a function in Python?",
    "options": ["func", "def", "function", "lambda"],
    "correct_index": 1,
    "explanation": "'def' is the keyword used to define a function.",
    "difficulty": "basic",
}

INVALID_MCQ_JSON = {
    "question_text": "Which keyword defines a function in Python?",
    "options": ["only one"],  # invalid: needs 4 options
    "correct_index": 1,
    "explanation": "explanation",
    "difficulty": "basic",
}


class FakeClient:
    """Returns a scripted sequence of JSON responses, one per call."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def generate_json(self, model, prompt):
        response = self.responses[self.calls]
        self.calls += 1
        return response


def _run(client, max_retries=3):
    return generate_validated(
        client=client,
        prompt_template="topic={topic} difficulty={difficulty}",
        retry_suffix=" retry: {error}",
        payload_cls=MCQPayload,
        topic="Python",
        difficulty="basic",
        max_retries=max_retries,
    )


def test_succeeds_on_first_try():
    client = FakeClient([VALID_MCQ_JSON])
    result = _run(client)
    assert result is not None
    assert client.calls == 1


def test_recovers_after_invalid_response_then_valid():
    client = FakeClient([INVALID_MCQ_JSON, INVALID_MCQ_JSON, VALID_MCQ_JSON])
    result = _run(client, max_retries=3)
    assert result is not None
    assert client.calls == 3


def test_gives_up_after_max_retries_and_returns_none():
    client = FakeClient([INVALID_MCQ_JSON, INVALID_MCQ_JSON, INVALID_MCQ_JSON])
    result = _run(client, max_retries=3)
    assert result is None
    assert client.calls == 3  # never exceeds the bound


def test_never_returns_malformed_data():
    """Even if every attempt is invalid, the function must never return an unvalidated payload."""
    client = FakeClient([INVALID_MCQ_JSON] * 5)
    result = _run(client, max_retries=5)
    assert result is None
