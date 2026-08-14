from django.urls import path

from api.views_analytics import AnalyticsView
from api.views_auth import LoginView, LogoutView, SignupView, StatusView
from api.views_public import PublicLeaderboardView, PublicTopicsView
from api.views_quiz import GradeMCQView, GradeScenarioView, QuizStartView
from api.views_topics import TopicListCreateView, TopicUpdateView

urlpatterns = [
    path("auth/signup", SignupView.as_view()),
    path("auth/login", LoginView.as_view()),
    path("auth/logout", LogoutView.as_view()),
    path("auth/status", StatusView.as_view()),
    path("topics", TopicListCreateView.as_view()),
    path("topics/<int:topic_id>", TopicUpdateView.as_view()),
    path("quiz/start", QuizStartView.as_view()),
    path("quiz/grade/mcq", GradeMCQView.as_view()),
    path("quiz/grade/scenario", GradeScenarioView.as_view()),
    path("analytics", AnalyticsView.as_view()),
    # Public (no login) -- consumed by the landing page and other pre-auth screens.
    path("public/topics", PublicTopicsView.as_view()),
    path("public/leaderboard", PublicLeaderboardView.as_view()),
]
