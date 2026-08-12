from django.contrib import admin

from quizbank.models import Attempt, Profile, Question, QuestionSeen, Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("display_name", "name", "is_active", "question_count", "created_at")
    list_editable = ("is_active",)
    search_fields = ("name", "display_name")
    list_filter = ("is_active",)

    @admin.display(description="Questions")
    def question_count(self, obj: Topic) -> int:
        return obj.questions.count()


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "attempt_count", "created_at")
    search_fields = ("name",)

    @admin.display(description="Attempts")
    def attempt_count(self, obj: Profile) -> int:
        return obj.attempts.count()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "difficulty", "type", "short_text", "created_at")
    list_filter = ("topic", "difficulty", "type")
    search_fields = ("question_text",)
    autocomplete_fields = ("topic",)
    readonly_fields = ("embedding", "created_at")

    @admin.display(description="Question")
    def short_text(self, obj: Question) -> str:
        return obj.question_text[:80]


@admin.register(QuestionSeen)
class QuestionSeenAdmin(admin.ModelAdmin):
    list_display = ("profile", "question", "seen_at")
    list_filter = ("profile",)
    autocomplete_fields = ("profile", "question")


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "question", "is_correct", "score", "attempted_at")
    list_filter = ("is_correct", "profile")
    autocomplete_fields = ("profile", "question")


admin.site.site_header = "SkillDrill Admin"
admin.site.site_title = "SkillDrill Admin"
admin.site.index_title = "Question bank & practice data"
