import anthropic
import logging
from sqlalchemy.orm import Session
from app.models import Article, Score
from app.config import settings
from app.progress import update_progress
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

logger = logging.getLogger(__name__)

def generate_summaries(db: Session, articles: list[Article]):
    if not settings.anthropic_api_key:
        logger.warning("No Anthropic API key found. Skipping summarization.")
        return
        
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    
    # Filter articles needing summary
    needs_summary = []
    for article in articles:
        if article.score and not article.score.summary:
            needs_summary.append(article)
        elif article.score and article.score.summary:
            logger.info(f"Summary already exists for {article.title}")
            
    total = len(needs_summary)
    if total == 0:
        return
        
    def fetch_summary(title: str, text: str) -> str:
        prompt = (
            f"You are a helpful news assistant. Summarize the following article into 2-3 concise, "
            f"informative sentences. Do not use clickbait language.\n\n"
            f"Title: {title}\n"
            f"Text: {text[:2000]}"
        )
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_article = {
            executor.submit(fetch_summary, a.title, a.raw_text): a
            for a in needs_summary
        }
        
        completed = 0
        for future in as_completed(future_to_article):
            article = future_to_article[future]
            completed += 1
            
            # Progress starts at 60%, goes up to 95%
            progress_pct = 60 + int((completed / total) * 35)
            update_progress(f"Generating summaries ({completed}/{total})", progress_pct)
            
            try:
                summary = future.result()
                article.score.summary = summary
                db.commit()
            except Exception as e:
                logger.error(f"Error generating summary for article {article.id}: {e}")
                db.rollback()
