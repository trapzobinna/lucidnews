import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.pipeline import run_daily_pipeline

logger = logging.getLogger(__name__)

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run every morning at 6:00 AM
    scheduler.add_job(
        run_daily_pipeline,
        trigger=CronTrigger(hour=6, minute=0),
        id="daily_pipeline_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Background scheduler started: Daily pipeline scheduled for 06:00 AM")
