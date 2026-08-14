import pytest

from quizbank.models import Question, QuestionSeen, Topic
from quizbank.quiz_selection import select_quiz_questions

pytestmark = pytest.mark.django_db


@pytest.fixture
def profile(make_profile):
    return make_profile("tester")


@pytest.fixture
def topic():
    return Topic.objects.create(name="python", display_name="Python")


def make_questions(topic, n, difficulty="basic"):
    made = []
    for i in range(n):
        made.append(
            Question.objects.create(
                topic=topic,
                difficulty=difficulty,
                type=Question.MCQ,
                question_text=f"Question {i}",
                options=["a", "b", "c", "d"],
                correct_index=0,
                explanation="because",
            )
        )
    return made


def test_selects_requested_count_when_enough_available(profile, topic):
    make_questions(topic, 5)
    questions = select_quiz_questions(profile.id, topic.id, "basic", count=3)
    assert len(questions) == 3


def test_returns_fewer_than_requested_when_bank_is_short(profile, topic):
    make_questions(topic, 2)
    questions = select_quiz_questions(profile.id, topic.id, "basic", count=5)
    assert len(questions) == 2


def test_marks_selected_questions_as_seen_for_profile(profile, topic):
    make_questions(topic, 3)
    questions = select_quiz_questions(profile.id, topic.id, "basic", count=3)

    seen_ids = set(
        QuestionSeen.objects.filter(profile_id=profile.id).values_list("question_id", flat=True)
    )
    assert seen_ids == {q.id for q in questions}


def test_prefers_unseen_questions_over_seen(profile, topic):
    questions = make_questions(topic, 4)
    # Mark the first 2 as already seen by this profile.
    for q in questions[:2]:
        QuestionSeen.objects.create(profile=profile, question=q)

    selected = select_quiz_questions(profile.id, topic.id, "basic", count=2)
    selected_ids = {q.id for q in selected}
    unseen_ids = {q.id for q in questions[2:]}
    assert selected_ids == unseen_ids


def test_falls_back_to_seen_questions_when_unseen_exhausted(profile, topic):
    questions = make_questions(topic, 2)
    for q in questions:
        QuestionSeen.objects.create(profile=profile, question=q)

    # Everything's seen, but a quiz should still be servable from the existing bank.
    selected = select_quiz_questions(profile.id, topic.id, "basic", count=2)
    assert len(selected) == 2


def test_only_returns_questions_matching_topic_and_difficulty(profile, topic):
    make_questions(topic, 2, difficulty="basic")
    make_questions(topic, 2, difficulty="mid")

    selected = select_quiz_questions(profile.id, topic.id, "basic", count=10)
    assert len(selected) == 2
    assert all(q.difficulty == "basic" for q in selected)
