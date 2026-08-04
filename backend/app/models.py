from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    display_name: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    questions: Mapped[list["Question"]] = relationship(back_populates="topic")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    difficulty: Mapped[str] = mapped_column(String(16))  # basic / mid
    type: Mapped[str] = mapped_column(String(16))  # mcq / scenario
    question_text: Mapped[str] = mapped_column(Text)

    # MCQ-only fields
    options: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    correct_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Scenario-only fields
    model_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    rubric: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    topic: Mapped["Topic"] = relationship(back_populates="questions")


class QuestionSeen(Base):
    """Per-profile record of which questions have already been served."""

    __tablename__ = "question_seen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    user_answer: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)  # scenario only, 0-100
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
