import os

from django.apps import AppConfig
from django.conf import settings


class QuizbankConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "quizbank"

    def ready(self):
        # runserver's autoreloader imports every app twice (once in the parent
        # watcher process, once in the reloaded child) -- only start the
        # scheduler in the process that's actually going to serve requests.
        if not settings.TOP_UP_ENABLED:
            return
        force = os.environ.get("SKILLDRILL_FORCE_SCHEDULER")
        if os.environ.get("RUN_MAIN") != "true" and not force:
            return

        from quizbank.scheduler import create_scheduler

        create_scheduler().start()
