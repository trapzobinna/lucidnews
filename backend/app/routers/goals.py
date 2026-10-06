from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserGoal
from app.schemas import UserGoalCreate, UserGoalResponse

router = APIRouter()

# Lazy-loaded embedder — only initialized when a goal is created
_embedder = None

def get_embedder():
    """Load the sentence-transformer model on first use.
    Keeps the API lightweight when ML deps aren't installed."""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError as e:
            raise HTTPException(
                status_code=503,
                detail="Embedding service unavailable on this instance. "
                       "Run the ML pipeline separately to create goals."
            ) from e
    return _embedder


@router.get("/", response_model=list[UserGoalResponse])
def get_goals(db: Session = Depends(get_db)):
    return db.query(UserGoal).filter(UserGoal.user_id == 1).all()


@router.post("/", response_model=UserGoalResponse)
def create_goal(goal: UserGoalCreate, db: Session = Depends(get_db)):
    embedder = get_embedder()
    emb = embedder.encode([goal.goal_text])[0]
    db_goal = UserGoal(
        user_id=1,
        goal_text=goal.goal_text,
        embedding_vector=emb.tobytes()
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(UserGoal).filter(UserGoal.id == goal_id, UserGoal.user_id == 1).first()
    if goal:
        db.delete(goal)
        db.commit()
    return {"success": True}
