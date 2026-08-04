import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.grading import grade_and_save_mcq, grade_and_save_scenario
from app.models import Base, Profile, Question, Topic


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


@pytest.fixture
def profile(session):
    p = Profile(name="tester")
    session.add(p)
    session.commit()
    return p


@pytest.fixture
def topic(session):
    t = Topic(name="python", display_name="Python")
    session.add(t)
    session.commit()
    return t


def make_mcq(session, topic, correct_index=1):
    q = Question(
        topic_id=topic.id,
        difficulty="basic",
        type="mcq",
        question_text="Which keyword defines a function?",
        options=["func", "def", "function", "lambda"],
        correct_index=correct_index,
        explanation="'def' defines a function.",
    )
    session.add(q)
    session.commit()
    return q


def make_scenario(session, topic, rubric=None):
    q = Question(
        topic_id=topic.id,
        difficulty="mid",
        type="scenario",
        question_text="A script crashes with IndexError. What do you check?",
        model_answer="Check bounds before indexing.",
        rubric=rubric or ["Checks list length", "Handles the edge case"],
    )
    session.add(q)
    session.commit()
    return q


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def generate_json(self, model, prompt):
        response = self.responses[self.calls]
        self.calls += 1
        return response


def test_mcq_correct_answer_marks_attempt_correct(session, profile, topic):
    q = make_mcq(session, topic, correct_index=1)
    attempt = grade_and_save_mcq(session, profile.id, q, selected_index=1)
    assert attempt.is_correct is True
    assert attempt.score is None


def test_mcq_wrong_answer_marks_attempt_incorrect(session, profile, topic):
    q = make_mcq(session, topic, correct_index=1)
    attempt = grade_and_save_mcq(session, profile.id, q, selected_index=0)
    assert attempt.is_correct is False


def test_mcq_attempt_is_persisted(session, profile, topic):
    q = make_mcq(session, topic, correct_index=2)
    grade_and_save_mcq(session, profile.id, q, selected_index=2)

    from sqlalchemy import select

    from app.models import Attempt

    saved = session.scalars(select(Attempt).where(Attempt.question_id == q.id)).one()
    assert saved.profile_id == profile.id
    assert saved.user_answer == "2"
    assert saved.is_correct is True


def test_scenario_grading_pass_above_threshold(session, profile, topic, monkeypatch):
    monkeypatch.setattr(settings, "scenario_pass_threshold", 70)
    q = make_scenario(session, topic)
    client = FakeClient([{"covered": [True, True], "score": 85, "feedback": "Solid answer."}])

    attempt, result = grade_and_save_scenario(client, session, profile.id, q, "check length first")

    assert attempt.is_correct is True
    assert attempt.score == 85
    assert result.covered == [True, True]


def test_scenario_grading_below_threshold_marked_incorrect(session, profile, topic, monkeypatch):
    monkeypatch.setattr(settings, "scenario_pass_threshold", 70)
    q = make_scenario(session, topic)
    client = FakeClient(
        [{"covered": [False, False], "score": 20, "feedback": "Missed the points."}]
    )

    attempt, result = grade_and_save_scenario(client, session, profile.id, q, "I dunno")

    assert attempt.is_correct is False
    assert attempt.score == 20


def test_scenario_grading_retries_on_covered_length_mismatch(session, profile, topic):
    q = make_scenario(session, topic)  # rubric has 2 points
    client = FakeClient(
        [
            {"covered": [True], "score": 90, "feedback": "wrong length"},  # invalid: 1 item
            {"covered": [True, False], "score": 60, "feedback": "corrected"},
        ]
    )

    attempt, result = grade_and_save_scenario(client, session, profile.id, q, "answer")

    assert client.calls == 2
    assert result.covered == [True, False]
    assert attempt.score == 60


def test_scenario_grading_gives_up_after_max_retries_and_saves_nothing(session, profile, topic):
    q = make_scenario(session, topic)
    client = FakeClient([{"covered": [True], "score": 90, "feedback": "always wrong length"}] * 3)

    outcome = grade_and_save_scenario(client, session, profile.id, q, "answer")

    assert outcome is None
    from sqlalchemy import select

    from app.models import Attempt

    assert session.scalars(select(Attempt)).all() == []
