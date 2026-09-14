import feedparser
from newspaper import Article as NewsArticle
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime
from time import mktime
import logging
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.models import Source, Article, UserGoal
from app.ingestion.sources import SOURCES
from app.progress import update_progress

logger = logging.getLogger(__name__)

# Initialize model for dedup
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def get_or_create_sources(db: Session):
    for s in SOURCES:
        db_source = db.query(Source).filter(Source.rss_url == s["rss_url"]).first()
        if not db_source:
            db_source = Source(
                name=s["name"],
                rss_url=s["rss_url"],
                base_credibility_score=s["base_credibility_score"],
                category=s["category"]
            )
            db.add(db_source)
            
    # Add dynamic Google News RSS feeds for user goals
    goals = db.query(UserGoal).all()
    for goal in goals:
        encoded_query = urllib.parse.quote(goal.goal_text)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        db_source = db.query(Source).filter(Source.rss_url == rss_url).first()
        if not db_source:
            db_source = Source(
                name=f"Google News: {goal.goal_text}",
                rss_url=rss_url,
                base_credibility_score=0.3, # Dynamic sources start with low baseline
                category="Dynamic"
            )
            db.add(db_source)
            
    db.commit()

def fetch_rss_feed(source: Source) -> list:
    feed = feedparser.parse(source.rss_url)
    entries = []
    
    # Cap dynamic sources to 10 results to bound processing time
    limit = 10 if source.category == "Dynamic" else len(feed.entries)
    
    for entry in feed.entries[:limit]:
        published = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published = datetime.fromtimestamp(mktime(entry.published_parsed))
        entries.append({
            "title": entry.title,
            "url": entry.link,
            "published_at": published
        })
    return entries

def extract_article_text(url: str, is_dynamic: bool = False) -> str | None:
    try:
        final_url = url
        if is_dynamic and "news.google.com" in url:
            # Resolve Google News redirect to get actual publisher URL
            try:
                res = requests.get(url, allow_redirects=True, timeout=5)
                final_url = res.url
            except Exception as re_err:
                logger.warning(f"Failed to resolve redirect for {url}: {re_err}")
                
        article = NewsArticle(final_url)
        article.download()
        article.parse()
        text = article.text.strip()
        return text if text else None
    except Exception as e:
        logger.error(f"Failed to extract text from {url}: {e}")
        return None

def is_duplicate(title: str, existing_titles: list[str], existing_embeddings: list, threshold: float = 0.85) -> bool:
    if not existing_titles:
        return False
    
    # Exact match fallback
    if title in existing_titles:
        return True
        
    new_embedding = embedder.encode([title])
    similarities = cosine_similarity(new_embedding, existing_embeddings)[0]
    
    return any(sim >= threshold for sim in similarities)

def run_ingestion(db: Session):
    logger.info("Starting ingestion run")
    get_or_create_sources(db)
    sources = db.query(Source).all()
    
    # For dedup within this run and recently in DB
    recent_articles = db.query(Article).order_by(Article.extracted_at.desc()).limit(200).all()
    existing_titles = [a.title for a in recent_articles]
    
    if existing_titles:
        existing_embeddings = embedder.encode(existing_titles)
    else:
        existing_embeddings = []
        
    added_count = 0
    all_entries = []
    
    # 1. Fetch all feeds sequentially (fast)
    for source in sources:
        logger.info(f"Fetching from {source.name}")
        try:
            entries = fetch_rss_feed(source)
            for entry in entries:
                all_entries.append((source, entry))
        except Exception as e:
            logger.error(f"Error fetching from {source.name}: {e}")
            
    # 2. Dedup against DB and each other
    valid_entries = []
    for source, entry in all_entries:
        if db.query(Article).filter(Article.url == entry["url"]).first():
            continue
            
        if is_duplicate(entry["title"], existing_titles, existing_embeddings):
            logger.info(f"Duplicate skipped: {entry['title']}")
            continue
            
        valid_entries.append((source, entry))
        existing_titles.append(entry["title"])
        new_emb = embedder.encode([entry["title"]])[0]
        if len(existing_embeddings) == 0:
            existing_embeddings = np.array([new_emb])
        else:
            existing_embeddings = np.vstack([existing_embeddings, new_emb])
            
    total_valid = len(valid_entries)
    if total_valid == 0:
        logger.info("Ingestion complete. No new articles to add.")
        return 0
        
    # 3. Parallel Extraction
    extracted_data = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_entry = {
            executor.submit(extract_article_text, entry["url"], source.category == "Dynamic"): (source, entry)
            for source, entry in valid_entries
        }
        
        completed = 0
        for future in as_completed(future_to_entry):
            source, entry = future_to_entry[future]
            completed += 1
            progress_pct = 10 + int((completed / total_valid) * 40)
            update_progress(f"Extracting articles ({completed}/{total_valid})", progress_pct)
            
            try:
                text = future.result()
                if text and len(text) >= 100:
                    extracted_data.append((source, entry, text))
                else:
                    logger.info(f"Skipped {entry['title']} due to short/empty text")
            except Exception as e:
                logger.error(f"Failed to extract text from {entry.get('url')}: {e}")
                
    # 4. DB Insertion (Sequential)
    for source, entry, text in extracted_data:
        try:
            new_article = Article(
                source_id=source.id,
                title=entry["title"],
                url=entry["url"],
                published_at=entry["published_at"],
                raw_text=text
            )
            db.add(new_article)
            db.commit()
            added_count += 1
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save article {entry.get('url')}: {e}")

    logger.info(f"Ingestion complete. Added {added_count} articles.")
    return added_count
