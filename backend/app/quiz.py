from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Question, QuestionSeen


def select_quiz_questions(
    session: Session, profile_id: int, topic_id: int, difficulty: str, count: int
) -> list[Question]:
    """Pick up to `count` questions for a quiz, preferring ones this profile hasn't
    seen yet. Marks every returned question as seen for this profile.
    """
    seen_ids = select(QuestionSeen.question_id).where(QuestionSeen.profile_id == profile_id)

    unseen = list(
        session.scalars(
            select(Question)
            .where(
                Question.topic_id == topic_id,
                Question.difficulty == difficulty,
                Question.id.not_in(seen_ids),
            )
            .order_by(func.random())
            .limit(count)
        ).all()
    )

    questions = unseen
    if len(questions) < count:
        remaining = count - len(questions)
        already_ids = [q.id for q in questions]
        seen_fill = session.scalars(
            select(Question)
            .where(
                Question.topic_id == topic_id,
                Question.difficulty == difficulty,
                Question.id.not_in(already_ids),
            )
            .order_by(func.random())
            .limit(remaining)
        ).all()
        questions.extend(seen_fill)

    for question in questions:
        session.add(QuestionSeen(profile_id=profile_id, question_id=question.id))
    session.commit()

    return questions
