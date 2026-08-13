import logging

from django import forms as dj_forms
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path

from llm.client import OllamaClient
from quizbank.forms import QuestionAdminForm
from quizbank.models import Attempt, Profile, Question, QuestionSeen, Topic
from quizbank.pipeline import generate_and_save_mcq_batch, generate_and_save_scenario_batch

logger = logging.getLogger("skilldrill.admin")


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


class GenerateQuestionsForm(dj_forms.Form):
    """Backs the 'Generate with AI' admin view.

    Deliberately minimal: topic, difficulty, and count only, all dropdowns.
    Generates `count` MCQs and `count` scenario questions for the chosen
    topic/difficulty by reusing the existing pipeline batch functions, so
    every generated question is embedded and checked for near-duplicates
    against the topic's full existing bank before it's saved.
    """

    topic = dj_forms.ModelChoiceField(
        queryset=Topic.objects.filter(is_active=True).order_by("display_name"),
        label="Topic",
    )
    difficulty = dj_forms.ChoiceField(choices=Question.DIFFICULTY_CHOICES)
    count = dj_forms.ChoiceField(
        choices=[(5, "5"), (10, "10"), (15, "15"), (20, "20")],
        label="Count (per question type)",
        help_text="Generates this many MCQs and this many scenario questions.",
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    list_display = ("id", "topic", "difficulty", "type", "short_text", "created_at")
    list_filter = ("topic", "difficulty", "type")
    search_fields = ("question_text",)
    autocomplete_fields = ("topic",)
    readonly_fields = ("embedding", "created_at")
    change_list_template = "admin/quizbank/question/change_list.html"

    fieldsets = (
        (None, {"fields": ("topic", "difficulty", "type", "question_text")}),
        (
            "MCQ fields",
            {
                "fields": ("options_text", "correct_index", "explanation"),
                "description": "Only used when Type = MCQ.",
            },
        ),
        (
            "Scenario fields",
            {
                "fields": ("model_answer", "rubric_text"),
                "description": "Only used when Type = Scenario.",
            },
        ),
        ("Metadata", {"fields": ("embedding", "created_at")}),
    )

    @admin.display(description="Question")
    def short_text(self, obj: Question) -> str:
        return obj.question_text[:80]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Manually-added questions still need an embedding, or they're invisible
        # to the near-duplicate check the AI pipeline runs (quizbank.dedup) the
        # next time this topic gets topped up or generated from.
        if not obj.embedding:
            try:
                client = OllamaClient()
                obj.embedding = client.embed(settings.OLLAMA_EMBEDDING_MODEL, obj.question_text)
                obj.save(update_fields=["embedding"])
            except Exception:
                logger.exception("failed to embed manually-added question id=%s", obj.id)
                messages.warning(
                    request,
                    "Question saved, but embedding failed (is Ollama reachable?) -- "
                    "it won't be checked for duplicates until re-saved.",
                )

    def get_urls(self):
        custom = [
            path(
                "generate/",
                self.admin_site.admin_view(self.generate_view),
                name="quizbank_question_generate",
            ),
        ]
        return custom + super().get_urls()

    def generate_view(self, request):
        """Generates `count` MCQs + `count` scenario questions for the chosen
        topic/difficulty via the existing pipeline, then redirects back to the
        changelist. Runs synchronously in the request -- fine for occasional
        manual use at these counts, but move to a background task if it starts
        timing out.
        """
        if request.method == "POST":
            form = GenerateQuestionsForm(request.POST)
            if form.is_valid():
                topic_obj = form.cleaned_data["topic"]
                difficulty = form.cleaned_data["difficulty"]
                count = int(form.cleaned_data["count"])

                client = OllamaClient()
                mcq_stats = generate_and_save_mcq_batch(client, topic_obj.name, difficulty, count)
                scenario_stats = generate_and_save_scenario_batch(
                    client, topic_obj.name, difficulty, count
                )

                messages.success(
                    request,
                    f"'{topic_obj.display_name}' ({difficulty}) -- "
                    f"MCQ: +{mcq_stats.saved} saved, {mcq_stats.skipped_invalid} invalid, "
                    f"{mcq_stats.skipped_duplicate} duplicate. "
                    f"Scenario: +{scenario_stats.saved} saved, "
                    f"{scenario_stats.skipped_invalid} invalid, "
                    f"{scenario_stats.skipped_duplicate} duplicate.",
                )
                return HttpResponseRedirect("..")
        else:
            form = GenerateQuestionsForm()

        context = {
            **self.admin_site.each_context(request),
            "form": form,
            "title": "Generate questions with AI",
            "opts": self.model._meta,
        }
        return render(request, "admin/quizbank/question/generate.html", context)


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
