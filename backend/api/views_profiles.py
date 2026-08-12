from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsPinAuthenticated
from api.serializers import ProfileCreateSerializer, ProfileSerializer
from quizbank.models import Profile


class ProfileListCreateView(APIView):
    permission_classes = [IsPinAuthenticated]

    def get(self, request: Request) -> Response:
        profiles = Profile.objects.all()
        return Response(ProfileSerializer(profiles, many=True).data)

    def post(self, request: Request) -> Response:
        body = ProfileCreateSerializer(data=request.data)
        body.is_valid(raise_exception=True)

        profile = Profile.objects.create(name=body.validated_data["name"].strip())
        return Response(ProfileSerializer(profile).data)
