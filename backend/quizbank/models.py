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
    name = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


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
