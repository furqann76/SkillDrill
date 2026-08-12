import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from django.db import close_old_connections

from llm.client import OllamaClient
from quizbank.topup import top_up_bank

logger = logging.getLogger("skilldrill.scheduler")


def run_top_up_job() -> None:
    # This runs on a background thread outside the request/response cycle, so
    # Django never gets a chance to recycle a stale connection on its own.
    close_old_connections()
    client = OllamaClient()
    try:
        results = top_up_bank(client)
        if not results:
            logger.info("bank top-up: everything already at or above the low watermark")
            return
        for topic_name, difficulty, qtype, stats in results:
            logger.info(
                "bank top-up: topic=%s difficulty=%s type=%s saved=%d "
                "skipped_invalid=%d skipped_duplicate=%d",
                topic_name,
                difficulty,
                qtype,
                stats.saved,
                stats.skipped_invalid,
                stats.skipped_duplicate,
            )
    except Exception:
        logger.exception("bank top-up job failed")
    finally:
        close_old_connections()


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    first_run = datetime.now() + timedelta(seconds=settings.TOP_UP_INITIAL_DELAY_SECONDS)
    scheduler.add_job(
        run_top_up_job,
        trigger=IntervalTrigger(minutes=settings.TOP_UP_INTERVAL_MINUTES),
        id="bank_top_up",
        next_run_time=first_run,
    )
    return scheduler
