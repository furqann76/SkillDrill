from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsAccountAuthenticated, IsStaffAuthenticated
from api.serializers import TopicCreateSerializer, TopicSerializer, TopicUpdateSerializer
from quizbank.models import Topic


class TopicListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsStaffAuthenticated()]
        return [IsAccountAuthenticated()]

    def get(self, request: Request) -> Response:
        include_inactive = request.query_params.get("include_inactive") == "true"
        topics = Topic.objects.all()
        if not include_inactive:
            topics = topics.filter(is_active=True)
        return Response(TopicSerializer(topics, many=True).data)

    def post(self, request: Request) -> Response:
        body = TopicCreateSerializer(data=request.data)
        body.is_valid(raise_exception=True)

        name = body.validated_data["name"].strip()
        if Topic.objects.filter(name=name).exists():
            return Response({"detail": f"Topic '{name}' already exists"}, status=409)

        display_name = (body.validated_data.get("display_name") or name).strip()
        topic = Topic.objects.create(name=name, display_name=display_name)
        return Response(TopicSerializer(topic).data)


class TopicUpdateView(APIView):
    permission_classes = [IsStaffAuthenticated]

    def patch(self, request: Request, topic_id: int) -> Response:
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response({"detail": "Topic not found"}, status=404)

        body = TopicUpdateSerializer(data=request.data)
        body.is_valid(raise_exception=True)

        topic.is_active = body.validated_data["is_active"]
        topic.save(update_fields=["is_active"])
        return Response(TopicSerializer(topic).data)
