import pytest
from pydantic import ValidationError

from llm.schemas import MCQPayload, ScenarioPayload

VALID_MCQ = {
    "question_text": "Which keyword defines a function in Python?",
    "options": ["func", "def", "function", "lambda"],
    "correct_index": 1,
    "explanation": "'def' is the keyword used to define a function.",
    "difficulty": "basic",
}

VALID_SCENARIO = {
    "question_text": "A junior dev's script crashes with an IndexError. What steps do they take?",
    "model_answer": "Check the list length before indexing, add bounds checking.",
    "rubric": ["Checks list length", "Handles the edge case", "Explains root cause"],
    "difficulty": "mid",
}


def test_valid_mcq_passes():
    payload = MCQPayload.model_validate(VALID_MCQ)
    assert payload.correct_index == 1
    assert len(payload.options) == 4


@pytest.mark.parametrize(
    "override",
    [
        {"options": ["a", "b", "c"]},  # only 3 options
        {"options": ["a", "b", "c", "d", "e"]},  # 5 options
        {"options": ["same", "same", "b", "c"]},  # duplicate options
        {"options": ["", "b", "c", "d"]},  # blank option
        {"correct_index": 4},  # out of range
        {"correct_index": -1},  # out of range
        {"question_text": "   "},  # blank question
        {"explanation": ""},  # blank explanation
        {"difficulty": "advanced"},  # invalid difficulty
    ],
)
def test_invalid_mcq_shapes_are_rejected(override):
    payload = {**VALID_MCQ, **override}
    with pytest.raises(ValidationError):
        MCQPayload.model_validate(payload)


def test_mcq_strips_whitespace_in_options():
    payload = MCQPayload.model_validate({**VALID_MCQ, "options": [" def ", "func", "fn", "lambda"]})
    assert payload.options[0] == "def"


def test_valid_scenario_passes():
    payload = ScenarioPayload.model_validate(VALID_SCENARIO)
    assert 2 <= len(payload.rubric) <= 4


@pytest.mark.parametrize(
    "override",
    [
        {"rubric": ["only one point"]},  # too few rubric points
        {"rubric": []},  # empty rubric
        {"rubric": ["a", "b", "c", "d", "e"]},  # too many rubric points
        {"question_text": ""},
        {"model_answer": "   "},
        {"difficulty": "expert"},
    ],
)
def test_invalid_scenario_shapes_are_rejected(override):
    payload = {**VALID_SCENARIO, **override}
    with pytest.raises(ValidationError):
        ScenarioPayload.model_validate(payload)
