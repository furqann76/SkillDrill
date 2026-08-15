from django.contrib.auth import authenticate, get_user, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import LoginRequestSerializer, ProfileSerializer, SignupRequestSerializer
from quizbank.models import Profile, get_or_create_profile


def _profile_data(user: User) -> dict:
    # Accounts made outside the signup flow (createsuperuser, a future
    # admin-added user) reach this without a Profile yet -- provision one
    # instead of leaving the frontend stuck on a null profile.
    return ProfileSerializer(get_or_create_profile(user)).data


class SignupView(APIView):
    def post(self, request: Request) -> Response:
        body = SignupRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data

        username = data["username"].strip()
        email = data["email"].strip().lower()

        if not username:
            return Response({"detail": "Username is required"}, status=400)
        if data["password"] != data["confirm_password"]:
            return Response({"detail": "Passwords do not match"}, status=400)
        if User.objects.filter(username__iexact=username).exists():
            return Response({"detail": "That username is already taken"}, status=409)
        if User.objects.filter(email__iexact=email).exists():
            return Response({"detail": "An account with that email already exists"}, status=409)

        try:
            # Pass an unsaved User with the candidate username/email so
            # UserAttributeSimilarityValidator can actually compare against
            # them -- without a user, that validator silently skips itself.
            validate_password(data["password"], user=User(username=username, email=email))
        except ValidationError as exc:
            return Response({"detail": " ".join(exc.messages)}, status=400)

        user = User.objects.create_user(username=username, email=email, password=data["password"])
        Profile.objects.create(
            user=user, name=username, preferred_topic=data.get("preferred_topic", "")
        )

        login(request, user)
        return Response({"profile": _profile_data(user)}, status=201)


class LoginView(APIView):
    def post(self, request: Request) -> Response:
        body = LoginRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data
        identifier = data["identifier"].strip()

        username = identifier
        if "@" in identifier:
            try:
                username = User.objects.get(email__iexact=identifier).username
            except User.DoesNotExist:
                pass  # fall through to authenticate() failing on the bad identifier

        user = authenticate(request, username=username, password=data["password"])
        if user is None:
            return Response({"detail": "Incorrect email/username or password"}, status=401)

        login(request, user)
        if not data["remember"]:
            request.session.set_expiry(0)  # expires when the browser closes

        return Response({"profile": _profile_data(user)})


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        logout(request)
        return Response({"ok": True})


class StatusView(APIView):
    def get(self, request: Request) -> Response:
        user = get_user(request)
        if not user.is_authenticated:
            return Response({"authenticated": False, "profile": None})
        return Response({"authenticated": True, "profile": _profile_data(user)})
