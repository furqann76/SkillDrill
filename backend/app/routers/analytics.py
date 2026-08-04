from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.analytics import compute_topic_stats, weak_topics
from app.config import settings
from app.deps import db_session, require_auth

router = APIRouter(
    prefix="/api/analytics", tags=["analytics"], dependencies=[Depends(require_auth)]
)


class TopicStatsOut(BaseModel):
    topic: str
    display_name: str
    total_attempts: int
    accuracy_pct: float | None
    mcq_accuracy_pct: float | None
    scenario_accuracy_pct: float | None


class AnalyticsResponse(BaseModel):
    topics: list[TopicStatsOut]
    weak_topics: list[str]


@router.get("/{profile_id}", response_model=AnalyticsResponse)
def get_analytics(profile_id: int, session: Session = Depends(db_session)) -> AnalyticsResponse:
    stats = compute_topic_stats(session, profile_id)
    weak = weak_topics(stats, settings.weak_topic_threshold)

    return AnalyticsResponse(
        topics=[
            TopicStatsOut(
                topic=s.topic,
                display_name=s.display_name,
                total_attempts=s.total_attempts,
                accuracy_pct=s.accuracy_pct,
                mcq_accuracy_pct=s.mcq_accuracy_pct,
                scenario_accuracy_pct=s.scenario_accuracy_pct,
            )
            for s in stats
        ],
        weak_topics=[s.display_name for s in weak],
    )
