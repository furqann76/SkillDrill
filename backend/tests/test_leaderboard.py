import pytest

from quizbank.leaderboard import compute_leaderboard
from quizbank.models import Attempt, Profile, Question, Topic

pytestmark = pytest.mark.django_db


@pytest.fixture
def topic():
    return Topic.objects.create(name="python", display_name="Python")


def make_question(topic):
    return Question.objects.create(
        topic=topic,
        difficulty="basic",
        type=Question.MCQ,
        question_text="Q",
        options=["a", "b", "c", "d"],
        correct_index=0,
        explanation="because",
    )


def make_attempts(profile, topic, correct_count, incorrect_count):
    for _ in range(correct_count):
        Attempt.objects.create(
            profile=profile, question=make_question(topic), user_answer="0", is_correct=True
        )
    for _ in range(incorrect_count):
        Attempt.objects.create(
            profile=profile, question=make_question(topic), user_answer="1", is_correct=False
        )


def test_empty_when_no_profiles_qualify(topic):
    p = Profile.objects.create(name="rookie")
    make_attempts(p, topic, correct_count=1, incorrect_count=0)  # only 1 attempt

    assert compute_leaderboard(min_attempts=5) == []


def test_ranks_by_accuracy_descending(topic):
    strong = Profile.objects.create(name="strong")
    make_attempts(strong, topic, correct_count=9, incorrect_count=1)  # 90%

    weak = Profile.objects.create(name="weak")
    make_attempts(weak, topic, correct_count=5, incorrect_count=5)  # 50%

    board = compute_leaderboard(min_attempts=5)

    assert [e.name for e in board] == ["strong", "weak"]
    assert board[0].rank == 1
    assert board[0].accuracy_pct == 90.0
    assert board[1].rank == 2
    assert board[1].accuracy_pct == 50.0


def test_excludes_profiles_below_min_attempts(topic):
    qualifies = Profile.objects.create(name="qualifies")
    make_attempts(qualifies, topic, correct_count=5, incorrect_count=0)

    too_few = Profile.objects.create(name="too_few")
    make_attempts(too_few, topic, correct_count=3, incorrect_count=0)

    board = compute_leaderboard(min_attempts=5)

    assert [e.name for e in board] == ["qualifies"]


def test_ties_broken_by_more_attempts_first(topic):
    fewer = Profile.objects.create(name="fewer")
    make_attempts(fewer, topic, correct_count=5, incorrect_count=5)  # 50%, 10 attempts

    more = Profile.objects.create(name="more")
    make_attempts(more, topic, correct_count=10, incorrect_count=10)  # 50%, 20 attempts

    board = compute_leaderboard(min_attempts=5)

    assert [e.name for e in board] == ["more", "fewer"]


def test_limit_caps_results(topic):
    for i in range(5):
        p = Profile.objects.create(name=f"user{i}")
        make_attempts(p, topic, correct_count=5, incorrect_count=0)

    board = compute_leaderboard(min_attempts=5, limit=3)

    assert len(board) == 3
    assert [e.rank for e in board] == [1, 2, 3]


def test_profile_with_zero_attempts_excluded_not_crashed(topic):
    Profile.objects.create(name="never-played")

    assert compute_leaderboard(min_attempts=1) == []
