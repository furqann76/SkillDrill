from django.contrib.auth import get_user
from rest_framework.permissions import BasePermission


class IsAccountAuthenticated(BasePermission):
    """Real, DB-backed session auth (django.contrib.auth), resolved directly
    from the session rather than through DRF's authentication-class layer --
    that keeps DRF's APIView csrf_exempt behavior intact for writes, matching
    how this same-origin, SameSite=Lax local app already handled the old PIN
    check, instead of introducing X-CSRFToken plumbing on the frontend.
    """

    def has_permission(self, request, view) -> bool:
        return get_user(request).is_authenticated
