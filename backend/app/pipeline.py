import logging
from datetime import date
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Briefing
from app.ingestion.ingest import run_ingestion
from app.ranking.ranker import run_scoring_and_ranking
from app.briefing.generate import generate_summaries
from app.progress import update_progress, set_error, complete_run
import json

# Ensure logging is setup
import app.logging_config

logger = logging.getLogger(__name__)

def run_daily_pipeline():
    logger.info("=== Starting Daily Pipeline ===")
    db: Session = SessionLocal()
    try:
        # 1. Ingestion
        update_progress("Ingestion", 10)
        run_ingestion(db)
        
        # 2. Scoring & Ranking
        update_progress("Scoring", 50)
        top_articles = run_scoring_and_ranking(db, top_n=8)
        
        if not top_articles:
            logger.warning("No articles selected for today's briefing")
            # Don't abort here. Skip summarization and save an empty briefing so frontend knows it ran.
        else:
            # 3. Summarization
            update_progress("Summarization", 60)
            generate_summaries(db, top_articles)
        
        # 4. Save Briefing
        update_progress("Saving", 95)
        today = date.today()
        # Check if today's briefing exists for default user (user_id=1)
        existing_briefing = db.query(Briefing).filter(Briefing.user_id == 1, Briefing.date == today).first()
        
        article_ids_json = json.dumps([a.id for a in top_articles])
        
        if existing_briefing:
            logger.info("Updating today's existing briefing")
            existing_briefing.article_ids = article_ids_json
        else:
            logger.info("Creating new briefing for today")
            new_briefing = Briefing(
                user_id=1,
                date=today,
                article_ids=article_ids_json
            )
            db.add(new_briefing)
            
        db.commit()
        logger.info("=== Daily Pipeline Completed Successfully ===")
        complete_run()
        
    except Exception as e:
        logger.exception("Pipeline failed")
        db.rollback()
        set_error(str(e))
    finally:
        db.close()

if __name__ == "__main__":
    run_daily_pipeline()
