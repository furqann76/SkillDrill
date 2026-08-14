import pytest

from quizbank.analytics import compute_topic_stats, weak_topics
from quizbank.models import Attempt, Question, Topic

pytestmark = pytest.mark.django_db


@pytest.fixture
def profile(make_profile):
    return make_profile("tester")


def make_topic(name):
    return Topic.objects.create(name=name, display_name=name)


def make_question(topic, qtype="mcq", difficulty="basic"):
    return Question.objects.create(
        topic=topic,
        difficulty=difficulty,
        type=qtype,
        question_text="Q",
        options=["a", "b", "c", "d"] if qtype == "mcq" else None,
        correct_index=0 if qtype == "mcq" else None,
        explanation="because" if qtype == "mcq" else None,
        model_answer="answer" if qtype == "scenario" else None,
        rubric=["point one", "point two"] if qtype == "scenario" else None,
    )


def make_attempt(profile, question, is_correct, score=None):
    return Attempt.objects.create(
        profile=profile,
        question=question,
        user_answer="0",
        is_correct=is_correct,
        score=score,
    )


def test_no_attempts_yields_no_stats(profile):
    make_topic("python")
    assert compute_topic_stats(profile.id) == []


def test_accuracy_computed_correctly(profile):
    topic = make_topic("python")
    q1 = make_question(topic)
    q2 = make_question(topic)
    q3 = make_question(topic)
    make_attempt(profile, q1, True)
    make_attempt(profile, q2, True)
    make_attempt(profile, q3, False)

    stats = compute_topic_stats(profile.id)
    assert len(stats) == 1
    assert stats[0].total_attempts == 3
    assert stats[0].correct_count == 2
    assert stats[0].accuracy_pct == pytest.approx(66.7, abs=0.1)


def test_mcq_and_scenario_accuracy_tracked_separately(profile):
    topic = make_topic("python")
    mcq = make_question(topic, qtype="mcq")
    scenario = make_question(topic, qtype="scenario")
    make_attempt(profile, mcq, True)
    make_attempt(profile, scenario, False)

    stats = compute_topic_stats(profile.id)
    assert stats[0].mcq_accuracy_pct == 100.0
    assert stats[0].scenario_accuracy_pct == 0.0


def test_stats_scoped_to_profile(profile, make_profile):
    other_profile = make_profile("other")

    topic = make_topic("python")
    q = make_question(topic)
    make_attempt(other_profile, q, True)

    assert compute_topic_stats(profile.id) == []


def test_multiple_topics_kept_separate(profile):
    python = make_topic("python")
    sql = make_topic("sql")
    make_attempt(profile, make_question(python), True)
    make_attempt(profile, make_question(sql), False)

    stats = compute_topic_stats(profile.id)
    by_name = {s.topic: s for s in stats}
    assert by_name["python"].accuracy_pct == 100.0
    assert by_name["sql"].accuracy_pct == 0.0


def test_weak_topics_below_threshold_only(profile):
    strong = make_topic("strong-topic")
    weak = make_topic("weak-topic")
    make_attempt(profile, make_question(strong), True)
    make_attempt(profile, make_question(weak), False)

    stats = compute_topic_stats(profile.id)
    weak_list = weak_topics(stats, threshold=70.0)

    assert len(weak_list) == 1
    assert weak_list[0].topic == "weak-topic"


def test_weak_topics_excludes_topics_with_no_attempts(profile):
    make_topic("untouched")
    assert weak_topics(compute_topic_stats(profile.id), threshold=70.0) == []


def test_weak_topics_sorted_worst_first(profile):
    ok = make_topic("ok-topic")
    bad = make_topic("bad-topic")
    # ok-topic: 1/2 correct = 50%; bad-topic: 0/2 correct = 0%
    make_attempt(profile, make_question(ok), True)
    make_attempt(profile, make_question(ok), False)
    make_attempt(profile, make_question(bad), False)
    make_attempt(profile, make_question(bad), False)

    weak_list = weak_topics(compute_topic_stats(profile.id), threshold=70.0)
    assert [w.topic for w in weak_list] == ["bad-topic", "ok-topic"]
