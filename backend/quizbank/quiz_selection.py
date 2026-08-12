from quizbank.models import Question, QuestionSeen


def select_quiz_questions(
    profile_id: int, topic_id: int, difficulty: str, count: int
) -> list[Question]:
    """Pick up to `count` questions for a quiz, preferring ones this profile hasn't
    seen yet. Marks every returned question as seen for this profile.
    """
    seen_ids = QuestionSeen.objects.filter(profile_id=profile_id).values_list(
        "question_id", flat=True
    )

    base = Question.objects.filter(topic_id=topic_id, difficulty=difficulty)
    questions = list(base.exclude(id__in=seen_ids).order_by("?")[:count])

    if len(questions) < count:
        remaining = count - len(questions)
        already_ids = [q.id for q in questions]
        seen_fill = list(base.exclude(id__in=already_ids).order_by("?")[:remaining])
        questions.extend(seen_fill)

    QuestionSeen.objects.bulk_create(
        [QuestionSeen(profile_id=profile_id, question_id=q.id) for q in questions]
    )

    return questions
