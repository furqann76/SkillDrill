from dataclasses import dataclass

from django.db.models import Count, Q

from quizbank.models import Profile


@dataclass
class LeaderboardEntry:
    rank: int
    name: str
    accuracy_pct: float
    total_attempts: int


def compute_leaderboard(min_attempts: int = 5, limit: int | None = None) -> list[LeaderboardEntry]:
    """Ranks profiles by overall accuracy across all their attempts, best first.

    Profiles with fewer than `min_attempts` are excluded so a single lucky (or
    unlucky) early attempt can't dominate the rankings. Ties break on total
    attempts (more attempts at the same accuracy ranks higher -- it's a more
    proven result).
    """
    profiles = Profile.objects.annotate(
        total=Count("attempts"),
        correct=Count("attempts", filter=Q(attempts__is_correct=True)),
    ).filter(total__gte=min_attempts)

    scored = [(p.name, round(p.correct / p.total * 100, 1), p.total) for p in profiles]
    scored.sort(key=lambda row: (-row[1], -row[2]))

    if limit is not None:
        scored = scored[:limit]

    return [
        LeaderboardEntry(rank=i + 1, name=name, accuracy_pct=accuracy, total_attempts=total)
        for i, (name, accuracy, total) in enumerate(scored)
    ]
