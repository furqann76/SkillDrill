"""One-off import of data from the old FastAPI/SQLAlchemy SQLite database into
the new Django-managed schema, preserving primary keys so foreign keys still
line up. Reads the old file directly via sqlite3 -- it's a different ORM's
database, not something Django should ever be pointed at directly.
"""

import json
import sqlite3

from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_naive, make_aware

from quizbank.models import Attempt, Profile, Question, QuestionSeen, Topic


def _dt(value: str):
    parsed = parse_datetime(value)
    if parsed is None:
        return None
    return make_aware(parsed) if is_naive(parsed) else parsed


def _json(value):
    return json.loads(value) if value is not None else None


class Command(BaseCommand):
    help = "Import topics/profiles/questions/attempts from the old SQLite database."

    def add_arguments(self, parser):
        parser.add_argument("--source", required=True, help="Path to the old .db file")

    def handle(self, *args, **options):
        source = options["source"]
        try:
            conn = sqlite3.connect(source)
        except sqlite3.Error as exc:
            raise CommandError(f"Couldn't open {source}: {exc}") from exc
        conn.row_factory = sqlite3.Row

        topics = conn.execute("SELECT * FROM topics").fetchall()
        Topic.objects.bulk_create(
            [
                Topic(
                    id=r["id"],
                    name=r["name"],
                    display_name=r["display_name"],
                    is_active=bool(r["is_active"]),
                    created_at=_dt(r["created_at"]),
                )
                for r in topics
            ]
        )
        self.stdout.write(f"topics: {len(topics)}")

        profiles = conn.execute("SELECT * FROM profiles").fetchall()
        Profile.objects.bulk_create(
            [Profile(id=r["id"], name=r["name"], created_at=_dt(r["created_at"])) for r in profiles]
        )
        self.stdout.write(f"profiles: {len(profiles)}")

        questions = conn.execute("SELECT * FROM questions").fetchall()
        Question.objects.bulk_create(
            [
                Question(
                    id=r["id"],
                    topic_id=r["topic_id"],
                    difficulty=r["difficulty"],
                    type=r["type"],
                    question_text=r["question_text"],
                    options=_json(r["options"]),
                    correct_index=r["correct_index"],
                    explanation=r["explanation"],
                    model_answer=r["model_answer"],
                    rubric=_json(r["rubric"]),
                    embedding=_json(r["embedding"]),
                    created_at=_dt(r["created_at"]),
                )
                for r in questions
            ],
            batch_size=500,
        )
        self.stdout.write(f"questions: {len(questions)}")

        seen = conn.execute("SELECT * FROM question_seen").fetchall()
        QuestionSeen.objects.bulk_create(
            [
                QuestionSeen(
                    id=r["id"],
                    profile_id=r["profile_id"],
                    question_id=r["question_id"],
                    seen_at=_dt(r["seen_at"]),
                )
                for r in seen
            ]
        )
        self.stdout.write(f"question_seen: {len(seen)}")

        attempts = conn.execute("SELECT * FROM attempts").fetchall()
        Attempt.objects.bulk_create(
            [
                Attempt(
                    id=r["id"],
                    profile_id=r["profile_id"],
                    question_id=r["question_id"],
                    user_answer=r["user_answer"],
                    is_correct=bool(r["is_correct"]),
                    score=r["score"],
                    attempted_at=_dt(r["attempted_at"]),
                )
                for r in attempts
            ]
        )
        self.stdout.write(f"attempts: {len(attempts)}")

        conn.close()
        self.stdout.write(self.style.SUCCESS("Import complete."))
