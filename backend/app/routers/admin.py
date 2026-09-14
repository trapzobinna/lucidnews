from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Article, Score
from app.pipeline import run_daily_pipeline
from app.progress import start_run, get_state
from fastapi import HTTPException
import json

router = APIRouter()

@router.post("/run-pipeline")
def trigger_pipeline(background_tasks: BackgroundTasks):
    if not start_run():
        raise HTTPException(status_code=409, detail="A pipeline is already running.")
    background_tasks.add_task(run_daily_pipeline)
    return {"message": "Pipeline triggered in background"}

@router.get("/pipeline-progress")
def get_pipeline_progress():
    return get_state()

@router.get("/excluded")
def get_excluded_articles(db: Session = Depends(get_db)):
    # Articles with scores that didn't make the cut (e.g. relevance < 0.3 or credibility < 0.6)
    # Since we can't easily query derived rank without complex logic, we'll fetch recently scored ones
    # that are not in today's briefing
    
    scored_articles = db.query(Article).join(Score).order_by(Article.extracted_at.desc()).limit(100).all()
    
    excluded = []
    for a in scored_articles:
        score = a.score
        if score.credibility_score < 0.6 or score.relevance_score < 0.3:
            excluded.append({
                "title": a.title,
                "url": a.url,
                "source": a.source.name,
                "category": a.source.category if a.source.category else "Uncategorized",
                "credibility_score": score.credibility_score,
                "relevance_score": score.relevance_score,
                "credibility_reasons": json.loads(score.credibility_reasons) if score.credibility_reasons else []
            })
            
    return excluded
