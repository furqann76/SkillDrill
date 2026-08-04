import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import Base, Profile, Question, QuestionSeen, Topic
from app.quiz import select_quiz_questions


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


def make_questions(session, topic, n, difficulty="basic"):
    made = []
    for i in range(n):
        q = Question(
            topic_id=topic.id,
            difficulty=difficulty,
            type="mcq",
            question_text=f"Question {i}",
            options=["a", "b", "c", "d"],
            correct_index=0,
            explanation="because",
        )
        session.add(q)
        made.append(q)
    session.commit()
    return made


def test_selects_requested_count_when_enough_available(session, profile, topic):
    make_questions(session, topic, 5)
    questions = select_quiz_questions(session, profile.id, topic.id, "basic", count=3)
    assert len(questions) == 3


def test_returns_fewer_than_requested_when_bank_is_short(session, profile, topic):
    make_questions(session, topic, 2)
    questions = select_quiz_questions(session, profile.id, topic.id, "basic", count=5)
    assert len(questions) == 2


def test_marks_selected_questions_as_seen_for_profile(session, profile, topic):
    make_questions(session, topic, 3)
    questions = select_quiz_questions(session, profile.id, topic.id, "basic", count=3)

    seen_ids = set(
        session.scalars(
            select(QuestionSeen.question_id).where(QuestionSeen.profile_id == profile.id)
        ).all()
    )
    assert seen_ids == {q.id for q in questions}


def test_prefers_unseen_questions_over_seen(session, profile, topic):
    questions = make_questions(session, topic, 4)
    # Mark the first 2 as already seen by this profile.
    for q in questions[:2]:
        session.add(QuestionSeen(profile_id=profile.id, question_id=q.id))
    session.commit()

    selected = select_quiz_questions(session, profile.id, topic.id, "basic", count=2)
    selected_ids = {q.id for q in selected}
    unseen_ids = {q.id for q in questions[2:]}
    assert selected_ids == unseen_ids


def test_falls_back_to_seen_questions_when_unseen_exhausted(session, profile, topic):
    questions = make_questions(session, topic, 2)
    for q in questions:
        session.add(QuestionSeen(profile_id=profile.id, question_id=q.id))
    session.commit()

    # Everything's seen, but a quiz should still be servable from the existing bank.
    selected = select_quiz_questions(session, profile.id, topic.id, "basic", count=2)
    assert len(selected) == 2


def test_only_returns_questions_matching_topic_and_difficulty(session, profile, topic):
    make_questions(session, topic, 2, difficulty="basic")
    make_questions(session, topic, 2, difficulty="mid")

    selected = select_quiz_questions(session, profile.id, topic.id, "basic", count=10)
    assert len(selected) == 2
    assert all(q.difficulty == "basic" for q in selected)
