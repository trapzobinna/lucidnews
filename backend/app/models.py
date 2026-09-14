from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Text, BLOB
from sqlalchemy.orm import relationship
from datetime import datetime
import json
from app.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rss_url = Column(String, unique=True, nullable=False, index=True)
    base_credibility_score = Column(Float, nullable=False)
    category = Column(String, nullable=False)

    articles = relationship("Article", back_populates="source")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False, index=True)
    published_at = Column(DateTime)
    raw_text = Column(Text, nullable=False)
    extracted_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("Source", back_populates="articles")
    score = relationship("Score", back_populates="article", uselist=False)


class UserGoal(Base):
    __tablename__ = "user_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=1)
    goal_text = Column(String, nullable=False)
    embedding_vector = Column(BLOB)  # Stored as numpy bytes

    scores = relationship("Score", back_populates="matched_goal")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), unique=True, nullable=False)
    credibility_score = Column(Float, nullable=False)
    credibility_reasons = Column(Text)  # Stored as JSON string
    relevance_score = Column(Float, nullable=False)
    relevance_match_type = Column(String, default="semantic")
    matched_keyword = Column(String, nullable=True)
    summary = Column(Text)
    matched_goal_id = Column(Integer, ForeignKey("user_goals.id"))

    article = relationship("Article", back_populates="score")
    matched_goal = relationship("UserGoal", back_populates="scores")


class Briefing(Base):
    __tablename__ = "briefings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=1)
    date = Column(Date, nullable=False)
    article_ids = Column(Text, nullable=False)  # JSON ordered list of IDs
    generated_at = Column(DateTime, default=datetime.utcnow)
