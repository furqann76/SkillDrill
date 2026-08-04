import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.analytics import compute_topic_stats, weak_topics
from app.models import Attempt, Base, Profile, Question, Topic


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


def make_topic(session, name):
    t = Topic(name=name, display_name=name)
    session.add(t)
    session.commit()
    return t


def make_question(session, topic, qtype="mcq", difficulty="basic"):
    q = Question(
        topic_id=topic.id,
        difficulty=difficulty,
        type=qtype,
        question_text="Q",
        options=["a", "b", "c", "d"] if qtype == "mcq" else None,
        correct_index=0 if qtype == "mcq" else None,
        explanation="because" if qtype == "mcq" else None,
        model_answer="answer" if qtype == "scenario" else None,
        rubric=["point one", "point two"] if qtype == "scenario" else None,
    )
    session.add(q)
    session.commit()
    return q


def make_attempt(session, profile, question, is_correct, score=None):
    a = Attempt(
        profile_id=profile.id,
        question_id=question.id,
        user_answer="0",
        is_correct=is_correct,
        score=score,
    )
    session.add(a)
    session.commit()
    return a


def test_no_attempts_yields_no_stats(session, profile):
    make_topic(session, "python")
    assert compute_topic_stats(session, profile.id) == []


def test_accuracy_computed_correctly(session, profile):
    topic = make_topic(session, "python")
    q1 = make_question(session, topic)
    q2 = make_question(session, topic)
    q3 = make_question(session, topic)
    make_attempt(session, profile, q1, True)
    make_attempt(session, profile, q2, True)
    make_attempt(session, profile, q3, False)

    stats = compute_topic_stats(session, profile.id)
    assert len(stats) == 1
    assert stats[0].total_attempts == 3
    assert stats[0].correct_count == 2
    assert stats[0].accuracy_pct == pytest.approx(66.7, abs=0.1)


def test_mcq_and_scenario_accuracy_tracked_separately(session, profile):
    topic = make_topic(session, "python")
    mcq = make_question(session, topic, qtype="mcq")
    scenario = make_question(session, topic, qtype="scenario")
    make_attempt(session, profile, mcq, True)
    make_attempt(session, profile, scenario, False)

    stats = compute_topic_stats(session, profile.id)
    assert stats[0].mcq_accuracy_pct == 100.0
    assert stats[0].scenario_accuracy_pct == 0.0


def test_stats_scoped_to_profile(session, profile):
    other_profile = Profile(name="other")
    session.add(other_profile)
    session.commit()

    topic = make_topic(session, "python")
    q = make_question(session, topic)
    make_attempt(session, other_profile, q, True)

    assert compute_topic_stats(session, profile.id) == []


def test_multiple_topics_kept_separate(session, profile):
    python = make_topic(session, "python")
    sql = make_topic(session, "sql")
    make_attempt(session, profile, make_question(session, python), True)
    make_attempt(session, profile, make_question(session, sql), False)

    stats = compute_topic_stats(session, profile.id)
    by_name = {s.topic: s for s in stats}
    assert by_name["python"].accuracy_pct == 100.0
    assert by_name["sql"].accuracy_pct == 0.0


def test_weak_topics_below_threshold_only(session, profile):
    strong = make_topic(session, "strong-topic")
    weak = make_topic(session, "weak-topic")
    make_attempt(session, profile, make_question(session, strong), True)
    make_attempt(session, profile, make_question(session, weak), False)

    stats = compute_topic_stats(session, profile.id)
    weak_list = weak_topics(stats, threshold=70.0)

    assert len(weak_list) == 1
    assert weak_list[0].topic == "weak-topic"


def test_weak_topics_excludes_topics_with_no_attempts(session, profile):
    make_topic(session, "untouched")
    assert weak_topics(compute_topic_stats(session, profile.id), threshold=70.0) == []


def test_weak_topics_sorted_worst_first(session, profile):
    ok = make_topic(session, "ok-topic")
    bad = make_topic(session, "bad-topic")
    # ok-topic: 1/2 correct = 50%; bad-topic: 0/2 correct = 0%
    make_attempt(session, profile, make_question(session, ok), True)
    make_attempt(session, profile, make_question(session, ok), False)
    make_attempt(session, profile, make_question(session, bad), False)
    make_attempt(session, profile, make_question(session, bad), False)

    weak_list = weak_topics(compute_topic_stats(session, profile.id), threshold=70.0)
    assert [w.topic for w in weak_list] == ["bad-topic", "ok-topic"]
