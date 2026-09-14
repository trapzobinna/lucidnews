from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime, date

class UserGoalBase(BaseModel):
    goal_text: str

class UserGoalCreate(UserGoalBase):
    pass

class UserGoalResponse(UserGoalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class ArticleBase(BaseModel):
    title: str
    url: str
    published_at: Optional[datetime]

class ScoreBase(BaseModel):
    credibility_score: float
    credibility_reasons: Optional[str]
    relevance_score: float
    matched_goal_id: Optional[int]

class SourceBase(BaseModel):
    name: str
    category: str

class BriefingItem(BaseModel):
    article: ArticleBase
    source: SourceBase
    score: ScoreBase
    summary: str  # Note: summary will be dynamically attached from Claude cache or another table. Wait, MVP says Claude summary. Let's adjust. We might need a summary column in scores or articles. The spec says "scores each... summarizes each into 2-3 sentences". We should add summary to scores table or briefings table. For now, we'll return it in the Briefing response.

class BriefingResponse(BaseModel):
    id: int
    date: date
    items: List[BriefingItem]

    class Config:
        from_attributes = True
