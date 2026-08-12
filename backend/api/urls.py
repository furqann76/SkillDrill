from django.urls import path

from api.views_analytics import AnalyticsView
from api.views_auth import LoginView, LogoutView, StatusView
from api.views_profiles import ProfileListCreateView
from api.views_quiz import GradeMCQView, GradeScenarioView, QuizStartView
from api.views_topics import TopicListCreateView, TopicUpdateView

urlpatterns = [
    path("auth/login", LoginView.as_view()),
    path("auth/logout", LogoutView.as_view()),
    path("auth/status", StatusView.as_view()),
    path("profiles", ProfileListCreateView.as_view()),
    path("topics", TopicListCreateView.as_view()),
    path("topics/<int:topic_id>", TopicUpdateView.as_view()),
    path("quiz/start", QuizStartView.as_view()),
    path("quiz/grade/mcq", GradeMCQView.as_view()),
    path("quiz/grade/scenario", GradeScenarioView.as_view()),
    path("analytics/<int:profile_id>", AnalyticsView.as_view()),
]
