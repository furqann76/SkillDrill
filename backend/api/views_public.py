from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from quizbank.leaderboard import compute_leaderboard
from quizbank.models import Topic


class PublicTopicsView(APIView):
    """Unauthenticated: active topic names for the public landing page's
    featured-topics section. Deliberately no permission_classes -- unlike
    api.views_topics.TopicListCreateView, which is the authenticated app's
    topic-management endpoint (list/create/activate).
    """

    def get(self, request: Request) -> Response:
        topics = Topic.objects.filter(is_active=True).order_by("display_name")
        return Response(
            [{"id": t.id, "name": t.name, "display_name": t.display_name} for t in topics]
        )


class PublicLeaderboardView(APIView):
    """Unauthenticated: profiles ranked by overall accuracy, for the landing
    page's leaderboard preview and the full /leaderboard page. `?limit=N`
    caps the result count (the preview uses a small limit; the full page
    omits it).
    """

    def get(self, request: Request) -> Response:
        limit_param = request.query_params.get("limit")
        limit = int(limit_param) if limit_param else None
        entries = compute_leaderboard(limit=limit)
        return Response(
            [
                {
                    "rank": e.rank,
                    "name": e.name,
                    "accuracy_pct": e.accuracy_pct,
                    "total_attempts": e.total_attempts,
                }
                for e in entries
            ]
        )
