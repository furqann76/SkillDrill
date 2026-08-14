import pytest
from django.contrib.auth.models import User

from quizbank.models import Profile


@pytest.fixture
def make_profile(db):
    """Profile is now 1:1 with a real account -- tests that need a profile
    need a backing User too."""

    def _make(name: str) -> Profile:
        user = User.objects.create_user(username=name, password="testpass123")
        return Profile.objects.create(user=user, name=name)

    return _make
