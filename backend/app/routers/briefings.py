from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import json

from app.database import get_db
from app.models import Briefing, Article
from app.schemas import BriefingResponse

router = APIRouter()

@router.get("/today", response_model=BriefingResponse)
def get_today_briefing(db: Session = Depends(get_db)):
    today = date.today()
    briefing = db.query(Briefing).filter(Briefing.user_id == 1, Briefing.date == today).first()
    
    if not briefing:
        raise HTTPException(status_code=404, detail="No briefing generated for today yet.")
        
    article_ids = json.loads(briefing.article_ids)
    
    # Fetch articles preserving order
    articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
    article_map = {a.id: a for a in articles}
    
    items = []
    for aid in article_ids:
        if aid in article_map:
            article = article_map[aid]
            items.append({
                "article": {
                    "title": article.title,
                    "url": article.url,
                    "published_at": article.published_at
                },
                "source": {
                    "name": article.source.name,
                    "category": article.source.category
                },
                "score": {
                    "credibility_score": article.score.credibility_score,
                    "credibility_reasons": article.score.credibility_reasons,
                    "relevance_score": article.score.relevance_score,
                    "relevance_match_type": getattr(article.score, 'relevance_match_type', 'semantic'),
                    "matched_keyword": getattr(article.score, 'matched_keyword', None),
                    "matched_goal_id": article.score.matched_goal_id
                },
                "summary": article.score.summary or "Summary not available."
            })
            
    return {
        "id": briefing.id,
        "date": briefing.date,
        "items": items
    }
