import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.db import get_session
from app.llm.client import OllamaClient
from app.topup import top_up_bank

logger = logging.getLogger("skilldrill.scheduler")


def run_top_up_job() -> None:
    session = get_session()
    client = OllamaClient()
    try:
        results = top_up_bank(session, client)
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
        session.close()


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    first_run = datetime.now() + timedelta(seconds=settings.top_up_initial_delay_seconds)
    scheduler.add_job(
        run_top_up_job,
        trigger=IntervalTrigger(minutes=settings.top_up_interval_minutes),
        id="bank_top_up",
        next_run_time=first_run,
    )
    return scheduler
