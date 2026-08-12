from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    pin = serializers.CharField()


class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()


class ProfileCreateSerializer(serializers.Serializer):
    name = serializers.CharField()


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
    profile_id = serializers.IntegerField()
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
    profile_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
    selected_index = serializers.IntegerField()


class GradeMCQResponseSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField()
    correct_index = serializers.IntegerField()
    explanation = serializers.CharField()


class GradeScenarioRequestSerializer(serializers.Serializer):
    profile_id = serializers.IntegerField()
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
