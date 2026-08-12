from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsPinAuthenticated
from quizbank.analytics import compute_topic_stats, weak_topics


class AnalyticsView(APIView):
    permission_classes = [IsPinAuthenticated]

    def get(self, request: Request, profile_id: int) -> Response:
        stats = compute_topic_stats(profile_id)
        weak = weak_topics(stats, settings.WEAK_TOPIC_THRESHOLD)

        return Response(
            {
                "topics": [
                    {
                        "topic": s.topic,
                        "display_name": s.display_name,
                        "total_attempts": s.total_attempts,
                        "accuracy_pct": s.accuracy_pct,
                        "mcq_accuracy_pct": s.mcq_accuracy_pct,
                        "scenario_accuracy_pct": s.scenario_accuracy_pct,
                    }
                    for s in stats
                ],
                "weak_topics": [s.display_name for s in weak],
            }
        )
