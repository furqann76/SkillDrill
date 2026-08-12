from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import LoginRequestSerializer


class LoginView(APIView):
    def post(self, request: Request) -> Response:
        body = LoginRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)

        if body.validated_data["pin"] != settings.APP_PIN:
            return Response({"detail": "Incorrect PIN"}, status=401)

        request.session["authenticated"] = True
        return Response({"ok": True})


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        request.session.flush()
        return Response({"ok": True})


class StatusView(APIView):
    def get(self, request: Request) -> Response:
        return Response({"authenticated": bool(request.session.get("authenticated"))})
