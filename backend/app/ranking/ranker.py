from sqlalchemy.orm import Session
from app.models import Article, Score, UserGoal
from app.scoring.credibility import score_credibility
from app.scoring.relevance import score_relevance
import logging

logger = logging.getLogger(__name__)

def run_scoring_and_ranking(db: Session, top_n: int = 8) -> list[Article]:
    logger.info("Starting scoring and ranking phase")
    # Get articles that don't have scores yet
    unscored_articles = db.query(Article).outerjoin(Score).filter(Score.id == None).all()
    
    # Get recently scored articles (to update relevance if goals changed)
    recently_scored_articles = db.query(Article).join(Score).order_by(Article.extracted_at.desc()).limit(200).all()
    
    goals = db.query(UserGoal).all()
    
    # Process new scores
    for article in unscored_articles:
        try:
            cred_score, cred_reasons = score_credibility(article, article.source)
            rel_score, matched_goal_id, match_type, matched_kw = score_relevance(article, goals)
            
            new_score = Score(
                article_id=article.id,
                credibility_score=cred_score,
                credibility_reasons=cred_reasons,
                relevance_score=rel_score,
                relevance_match_type=match_type,
                matched_keyword=matched_kw,
                matched_goal_id=matched_goal_id
            )
            db.add(new_score)
        except Exception as e:
            logger.error(f"Error scoring article {article.id}: {e}")
            
    # Re-score relevance for existing articles
    for article in recently_scored_articles:
        try:
            rel_score, matched_goal_id, match_type, matched_kw = score_relevance(article, goals)
            article.score.relevance_score = rel_score
            article.score.matched_goal_id = matched_goal_id
            article.score.relevance_match_type = match_type
            article.score.matched_keyword = matched_kw
        except Exception as e:
            logger.error(f"Error re-scoring relevance for article {article.id}: {e}")
            
    db.commit()
    
    # Ranking
    # For MVP: rank by (relevance * 0.7) + (credibility * 0.3)
    # Filter out articles with credibility < 0.6 or relevance < 0.3
    # Only rank from the recently processed pool to avoid surfacing old news
    all_scored = unscored_articles + recently_scored_articles
    
    ranked_list = []
    for article in all_scored:
        score = article.score
        if score.credibility_score >= 0.6 and score.relevance_score >= 0.3:
            final_rank = (score.relevance_score * 0.7) + (score.credibility_score * 0.3)
            ranked_list.append((final_rank, article))
            
    ranked_list.sort(key=lambda x: x[0], reverse=True)
    
    selected = [item[1] for item in ranked_list[:top_n]]
    logger.info(f"Selected {len(selected)} articles for briefing")
    return selected
