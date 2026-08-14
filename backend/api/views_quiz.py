from django.contrib.auth import get_user
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsAccountAuthenticated
from api.serializers import (
    GradeMCQRequestSerializer,
    GradeScenarioRequestSerializer,
    QuizStartRequestSerializer,
)
from llm.client import OllamaClient
from quizbank.grading import grade_and_save_mcq, grade_and_save_scenario
from quizbank.models import Question, Topic
from quizbank.quiz_selection import select_quiz_questions

_client = OllamaClient()


class QuizStartView(APIView):
    permission_classes = [IsAccountAuthenticated]

    def post(self, request: Request) -> Response:
        body = QuizStartRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data

        try:
            topic = Topic.objects.get(name=data["topic"])
        except Topic.DoesNotExist:
            return Response({"detail": f"Unknown topic: {data['topic']}"}, status=404)

        profile = get_user(request).profile
        questions = select_quiz_questions(profile.id, topic.id, data["difficulty"], data["count"])
        out = [
            {
                "id": q.id,
                "type": q.type,
                "difficulty": q.difficulty,
                "question_text": q.question_text,
                "options": q.options if q.type == Question.MCQ else None,
            }
            for q in questions
        ]
        return Response({"questions": out, "requested": data["count"], "available": len(out)})


class GradeMCQView(APIView):
    permission_classes = [IsAccountAuthenticated]

    def post(self, request: Request) -> Response:
        body = GradeMCQRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data

        try:
            question = Question.objects.get(id=data["question_id"], type=Question.MCQ)
        except Question.DoesNotExist:
            return Response({"detail": "MCQ question not found"}, status=404)

        profile = get_user(request).profile
        grade_and_save_mcq(profile.id, question, data["selected_index"])
        return Response(
            {
                "is_correct": data["selected_index"] == question.correct_index,
                "correct_index": question.correct_index,
                "explanation": question.explanation,
            }
        )


class GradeScenarioView(APIView):
    permission_classes = [IsAccountAuthenticated]

    def post(self, request: Request) -> Response:
        body = GradeScenarioRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data

        try:
            question = Question.objects.get(id=data["question_id"], type=Question.SCENARIO)
        except Question.DoesNotExist:
            return Response({"detail": "Scenario question not found"}, status=404)

        profile = get_user(request).profile
        outcome = grade_and_save_scenario(_client, profile.id, question, data["answer_text"])
        if outcome is None:
            return Response(
                {"detail": "Grading failed after retries; please try again"}, status=502
            )
        attempt, result = outcome

        breakdown = [
            {"point": point, "covered": covered}
            for point, covered in zip(question.rubric, result.covered, strict=True)
        ]
        return Response(
            {
                "score": result.score,
                "is_correct": attempt.is_correct,
                "rubric_breakdown": breakdown,
                "feedback": result.feedback,
                "model_answer": question.model_answer,
            }
        )
