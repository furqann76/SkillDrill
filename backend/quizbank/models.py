from django.conf import settings
from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=64, unique=True)
    display_name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self) -> str:
        return self.display_name


class Profile(models.Model):
    """One practice profile per account -- created automatically at signup,
    named after the account's username. Kept as a separate model (rather than
    folding its fields into User) because Attempt/QuestionSeen were already
    built against `profile`, and quiz/grading/analytics logic is naturally
    scoped to "whoever is practicing" independent of how they authenticated.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    name = models.CharField(max_length=64, unique=True)
    # Optional signup-time topic pick (by Topic.name), used to preselect the
    # quiz setup topic dropdown on first use. Never required.
    preferred_topic = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


def get_or_create_profile(user) -> "Profile":
    """Resolve a user's profile, creating one on first use if it's missing.

    Every account created through the public signup flow gets a Profile
    immediately, but accounts created outside that flow -- `createsuperuser`,
    a future admin-panel-added user -- never go through SignupView, so they'd
    otherwise 500 the first time they try to take a quiz.
    """
    profile, _ = Profile.objects.get_or_create(user=user, defaults={"name": user.username})
    return profile


class Question(models.Model):
    MCQ = "mcq"
    SCENARIO = "scenario"
    TYPE_CHOICES = [(MCQ, "MCQ"), (SCENARIO, "Scenario")]
    DIFFICULTY_CHOICES = [("basic", "Basic"), ("mid", "Mid")]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    difficulty = models.CharField(max_length=16, choices=DIFFICULTY_CHOICES)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    question_text = models.TextField()

    # MCQ-only
    options = models.JSONField(null=True, blank=True)
    correct_index = models.IntegerField(null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)

    # Scenario-only
    model_answer = models.TextField(null=True, blank=True)
    rubric = models.JSONField(null=True, blank=True)

    embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.question_text[:60]


class QuestionSeen(models.Model):
    """Per-profile record of which questions have already been served."""

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="seen_questions")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="seen_by")
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["profile", "question"])]


class Attempt(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="attempts")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="attempts")
    user_answer = models.TextField()
    is_correct = models.BooleanField()
    score = models.FloatField(null=True, blank=True)  # scenario only, 0-100
    attempted_at = models.DateTimeField(auto_now_add=True)
