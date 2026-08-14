import pytest
from django.conf import settings

from quizbank.grading import grade_and_save_mcq, grade_and_save_scenario
from quizbank.models import Attempt, Question, Topic

pytestmark = pytest.mark.django_db


@pytest.fixture
def profile(make_profile):
    return make_profile("tester")


@pytest.fixture
def topic():
    return Topic.objects.create(name="python", display_name="Python")


def make_mcq(topic, correct_index=1):
    return Question.objects.create(
        topic=topic,
        difficulty="basic",
        type=Question.MCQ,
        question_text="Which keyword defines a function?",
        options=["func", "def", "function", "lambda"],
        correct_index=correct_index,
        explanation="'def' defines a function.",
    )


def make_scenario(topic, rubric=None):
    return Question.objects.create(
        topic=topic,
        difficulty="mid",
        type=Question.SCENARIO,
        question_text="A script crashes with IndexError. What do you check?",
        model_answer="Check bounds before indexing.",
        rubric=rubric or ["Checks list length", "Handles the edge case"],
    )


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def generate_json(self, model, prompt):
        response = self.responses[self.calls]
        self.calls += 1
        return response


def test_mcq_correct_answer_marks_attempt_correct(profile, topic):
    q = make_mcq(topic, correct_index=1)
    attempt = grade_and_save_mcq(profile.id, q, selected_index=1)
    assert attempt.is_correct is True
    assert attempt.score is None


def test_mcq_wrong_answer_marks_attempt_incorrect(profile, topic):
    q = make_mcq(topic, correct_index=1)
    attempt = grade_and_save_mcq(profile.id, q, selected_index=0)
    assert attempt.is_correct is False


def test_mcq_attempt_is_persisted(profile, topic):
    q = make_mcq(topic, correct_index=2)
    grade_and_save_mcq(profile.id, q, selected_index=2)

    saved = Attempt.objects.get(question=q)
    assert saved.profile_id == profile.id
    assert saved.user_answer == "2"
    assert saved.is_correct is True


def test_scenario_grading_pass_above_threshold(profile, topic, monkeypatch):
    monkeypatch.setattr(settings, "SCENARIO_PASS_THRESHOLD", 70)
    q = make_scenario(topic)
    client = FakeClient([{"covered": [True, True], "score": 85, "feedback": "Solid answer."}])

    attempt, result = grade_and_save_scenario(client, profile.id, q, "check length first")

    assert attempt.is_correct is True
    assert attempt.score == 85
    assert result.covered == [True, True]


def test_scenario_grading_below_threshold_marked_incorrect(profile, topic, monkeypatch):
    monkeypatch.setattr(settings, "SCENARIO_PASS_THRESHOLD", 70)
    q = make_scenario(topic)
    client = FakeClient(
        [{"covered": [False, False], "score": 20, "feedback": "Missed the points."}]
    )

    attempt, result = grade_and_save_scenario(client, profile.id, q, "I dunno")

    assert attempt.is_correct is False
    assert attempt.score == 20


def test_scenario_grading_retries_on_covered_length_mismatch(profile, topic):
    q = make_scenario(topic)  # rubric has 2 points
    client = FakeClient(
        [
            {"covered": [True], "score": 90, "feedback": "wrong length"},  # invalid: 1 item
            {"covered": [True, False], "score": 60, "feedback": "corrected"},
        ]
    )

    attempt, result = grade_and_save_scenario(client, profile.id, q, "answer")

    assert client.calls == 2
    assert result.covered == [True, False]
    assert attempt.score == 60


def test_scenario_grading_gives_up_after_max_retries_and_saves_nothing(profile, topic):
    q = make_scenario(topic)
    client = FakeClient([{"covered": [True], "score": 90, "feedback": "always wrong length"}] * 3)

    outcome = grade_and_save_scenario(client, profile.id, q, "answer")

    assert outcome is None
    assert Attempt.objects.count() == 0
