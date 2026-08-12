from rest_framework.permissions import BasePermission


class IsPinAuthenticated(BasePermission):
    """Mirrors the old require_auth dependency: a truthy `authenticated` flag
    in the session, set by the /auth/login PIN check.
    """

    def has_permission(self, request, view) -> bool:
        return bool(request.session.get("authenticated"))
