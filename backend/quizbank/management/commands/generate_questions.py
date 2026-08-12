"""Generate questions for one topic/difficulty and save validated, deduplicated
results to the bank.

Usage:
    python manage.py generate_questions --topic Python --difficulty basic --count 10
    python manage.py generate_questions --topic Python --difficulty basic --count 10 --type scenario
"""

from django.core.management.base import BaseCommand

from llm.client import OllamaClient
from quizbank.pipeline import generate_and_save_mcq_batch, generate_and_save_scenario_batch


class Command(BaseCommand):
    help = "Generate and save validated, deduplicated questions for one topic/difficulty."

    def add_arguments(self, parser):
        parser.add_argument("--topic", required=True)
        parser.add_argument("--difficulty", required=True, choices=["basic", "mid"])
        parser.add_argument("--count", type=int, default=10)
        parser.add_argument("--type", choices=["mcq", "scenario"], default="mcq")

    def handle(self, *args, **options):
        client = OllamaClient()

        if options["type"] == "mcq":
            stats = generate_and_save_mcq_batch(
                client, options["topic"], options["difficulty"], options["count"]
            )
        else:
            stats = generate_and_save_scenario_batch(
                client, options["topic"], options["difficulty"], options["count"]
            )

        for q in stats.saved_questions:
            self.stdout.write(f"saved: {q.question_text[:80]}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. requested={options['count']} saved={stats.saved} "
                f"skipped_invalid={stats.skipped_invalid} "
                f"skipped_duplicate={stats.skipped_duplicate}"
            )
        )
