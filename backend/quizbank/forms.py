from django import forms

from quizbank.models import Question


class QuestionAdminForm(forms.ModelForm):
    """Admin form for Question that adapts to MCQ vs scenario shape.

    `options` and `rubric` are JSONFields on the model, but hand-typing JSON
    arrays in the admin is error-prone, so this form exposes them as
    one-item-per-line textareas and converts to/from lists in clean()/save().
    Only the fields relevant to the selected `type` are required/kept; the
    other type's fields are cleared out on save so stale data can't linger.
    """

    options_text = forms.CharField(
        label="Options (one per line, exactly 4)",
        widget=forms.Textarea(attrs={"rows": 4}),
        required=False,
        help_text="MCQ only. One option per line, in order.",
    )
    rubric_text = forms.CharField(
        label="Rubric (one key point per line, 2-4)",
        widget=forms.Textarea(attrs={"rows": 4}),
        required=False,
        help_text="Scenario only. One rubric point per line.",
    )

    class Meta:
        model = Question
        fields = [
            "topic",
            "difficulty",
            "type",
            "question_text",
            "options_text",
            "correct_index",
            "explanation",
            "model_answer",
            "rubric_text",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance and instance.pk:
            if instance.options:
                self.fields["options_text"].initial = "\n".join(instance.options)
            if instance.rubric:
                self.fields["rubric_text"].initial = "\n".join(instance.rubric)

    def clean(self):
        cleaned = super().clean()
        qtype = cleaned.get("type")

        if qtype == Question.MCQ:
            options_raw = cleaned.get("options_text", "") or ""
            options = [line.strip() for line in options_raw.splitlines() if line.strip()]
            if len(options) != 4:
                self.add_error("options_text", "MCQ requires exactly 4 options, one per line.")
            elif len(set(options)) != 4:
                self.add_error("options_text", "Options must be distinct.")
            cleaned["_options"] = options

            correct_index = cleaned.get("correct_index")
            if correct_index is None or not (0 <= correct_index <= 3):
                self.add_error("correct_index", "Must be an integer 0-3 for MCQ.")

            if not (cleaned.get("explanation") or "").strip():
                self.add_error("explanation", "Required for MCQ questions.")

        elif qtype == Question.SCENARIO:
            rubric_raw = cleaned.get("rubric_text", "") or ""
            rubric = [line.strip() for line in rubric_raw.splitlines() if line.strip()]
            if not (2 <= len(rubric) <= 4):
                self.add_error("rubric_text", "Scenario requires 2-4 rubric points, one per line.")
            cleaned["_rubric"] = rubric

            if not (cleaned.get("model_answer") or "").strip():
                self.add_error("model_answer", "Required for scenario questions.")

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.type == Question.MCQ:
            instance.options = self.cleaned_data.get("_options")
            instance.model_answer = None
            instance.rubric = None
        elif instance.type == Question.SCENARIO:
            instance.rubric = self.cleaned_data.get("_rubric")
            instance.options = None
            instance.correct_index = None
            instance.explanation = None

        if commit:
            instance.save()
        return instance
