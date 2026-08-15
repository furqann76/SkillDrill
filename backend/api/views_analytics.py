from django.conf import settings
from django.contrib.auth import get_user
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsAccountAuthenticated
from quizbank.analytics import compute_topic_stats, weak_topics
from quizbank.models import get_or_create_profile


class AnalyticsView(APIView):
    permission_classes = [IsAccountAuthenticated]

    def get(self, request: Request) -> Response:
        profile = get_or_create_profile(get_user(request))
        stats = compute_topic_stats(profile.id)
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
