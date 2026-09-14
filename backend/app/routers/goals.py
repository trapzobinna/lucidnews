from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserGoal
from app.schemas import UserGoalCreate, UserGoalResponse
from sentence_transformers import SentenceTransformer
import numpy as np

router = APIRouter()
embedder = SentenceTransformer('all-MiniLM-L6-v2')

@router.get("/", response_model=list[UserGoalResponse])
def get_goals(db: Session = Depends(get_db)):
    return db.query(UserGoal).filter(UserGoal.user_id == 1).all()

@router.post("/", response_model=UserGoalResponse)
def create_goal(goal: UserGoalCreate, db: Session = Depends(get_db)):
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
