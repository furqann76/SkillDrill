from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Attempt, Question, Topic


@dataclass
class TopicStats:
    topic: str
    display_name: str
    total_attempts: int = 0
    correct_count: int = 0
    mcq_attempts: int = 0
    mcq_correct: int = 0
    scenario_attempts: int = 0
    scenario_correct: int = 0

    @property
    def accuracy_pct(self) -> float | None:
        if not self.total_attempts:
            return None
        return round(self.correct_count / self.total_attempts * 100, 1)

    @property
    def mcq_accuracy_pct(self) -> float | None:
        if not self.mcq_attempts:
            return None
        return round(self.mcq_correct / self.mcq_attempts * 100, 1)

    @property
    def scenario_accuracy_pct(self) -> float | None:
        if not self.scenario_attempts:
            return None
        return round(self.scenario_correct / self.scenario_attempts * 100, 1)


def _record(stat: TopicStats, qtype: str, is_correct: bool) -> None:
    stat.total_attempts += 1
    if is_correct:
        stat.correct_count += 1
    if qtype == "mcq":
        stat.mcq_attempts += 1
        if is_correct:
            stat.mcq_correct += 1
    else:
        stat.scenario_attempts += 1
        if is_correct:
            stat.scenario_correct += 1


def compute_topic_stats(session: Session, profile_id: int) -> list[TopicStats]:
    """One row per topic this profile has attempted at least one question in."""
    rows = session.execute(
        select(Topic.name, Topic.display_name, Question.type, Attempt.is_correct)
        .join(Question, Question.topic_id == Topic.id)
        .join(Attempt, Attempt.question_id == Question.id)
        .where(Attempt.profile_id == profile_id)
    ).all()

    stats: dict[str, TopicStats] = {}
    for name, display_name, qtype, is_correct in rows:
        stat = stats.setdefault(name, TopicStats(topic=name, display_name=display_name))
        _record(stat, qtype, is_correct)

    return sorted(stats.values(), key=lambda s: s.topic)


def weak_topics(stats: list[TopicStats], threshold: float) -> list[TopicStats]:
    """Topics with attempts and accuracy below `threshold`, worst first."""
    candidates = [s for s in stats if s.accuracy_pct is not None and s.accuracy_pct < threshold]
    return sorted(candidates, key=lambda s: s.accuracy_pct)  # type: ignore[arg-type,return-value]
