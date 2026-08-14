from rest_framework import serializers


class SignupRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=64)
    email = serializers.EmailField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    preferred_topic = serializers.CharField(required=False, allow_blank=True, default="")


class LoginRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField()
    remember = serializers.BooleanField(required=False, default=False)


class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    preferred_topic = serializers.CharField(allow_blank=True)


class TopicSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    display_name = serializers.CharField()
    is_active = serializers.BooleanField()


class TopicCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    display_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class TopicUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()


class QuizStartRequestSerializer(serializers.Serializer):
    topic = serializers.CharField()
    difficulty = serializers.CharField()
    count = serializers.IntegerField(default=10)


class QuestionOutSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    difficulty = serializers.CharField()
    question_text = serializers.CharField()
    options = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)


class QuizStartResponseSerializer(serializers.Serializer):
    questions = QuestionOutSerializer(many=True)
    requested = serializers.IntegerField()
    available = serializers.IntegerField()


class GradeMCQRequestSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_index = serializers.IntegerField()


class GradeMCQResponseSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField()
    correct_index = serializers.IntegerField()
    explanation = serializers.CharField()


class GradeScenarioRequestSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_text = serializers.CharField()


class RubricPointSerializer(serializers.Serializer):
    point = serializers.CharField()
    covered = serializers.BooleanField()


class GradeScenarioResponseSerializer(serializers.Serializer):
    score = serializers.FloatField()
    is_correct = serializers.BooleanField()
    rubric_breakdown = RubricPointSerializer(many=True)
    feedback = serializers.CharField()
    model_answer = serializers.CharField()


class TopicStatsOutSerializer(serializers.Serializer):
    topic = serializers.CharField()
    display_name = serializers.CharField()
    total_attempts = serializers.IntegerField()
    accuracy_pct = serializers.FloatField(allow_null=True)
    mcq_accuracy_pct = serializers.FloatField(allow_null=True)
    scenario_accuracy_pct = serializers.FloatField(allow_null=True)


class AnalyticsResponseSerializer(serializers.Serializer):
    topics = TopicStatsOutSerializer(many=True)
    weak_topics = serializers.ListField(child=serializers.CharField())
