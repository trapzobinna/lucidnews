from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import Article, UserGoal

embedder = SentenceTransformer('all-MiniLM-L6-v2')

import re

def extract_keywords(goal_text: str) -> list[str]:
    # Strip stopwords and keep proper nouns or any explicitly requested keywords
    # For MVP, we'll just remove extremely common stopwords and keep words > 3 chars
    stopwords = {"this", "that", "with", "from", "your", "what", "have", "they", "will"}
    words = []
    for w in re.split(r'\W+', goal_text):
        if len(w) > 3 and w.lower() not in stopwords:
            words.append(w)
    return words

def keyword_match(article_text: str, keywords: list[str]) -> tuple[bool, str | None]:
    if not keywords:
        return False, None
    for kw in keywords:
        # Check literal keyword and basic variant forms (e.g. Nigeria, Nigerian)
        # Using word boundary and basic suffix matching
        pattern = r'\b' + re.escape(kw) + r'(n|an|ian|ese)?\b'
        if re.search(pattern, article_text, re.IGNORECASE):
            return True, kw
    return False, None

def score_relevance(article: Article, goals: list[UserGoal]) -> tuple[float, int | None, str, str | None]:
    if not goals:
        return 0.5, None, "semantic", None
        
    article_embedding = embedder.encode([article.title + ". " + article.raw_text[:500]])[0]
    
    best_score = -1.0
    best_goal_id = None
    best_match_type = "semantic"
    best_matched_keyword = None
    
    import numpy as np
    article_text = article.title + " " + article.raw_text
    
    for goal in goals:
        if goal.embedding_vector:
            goal_emb = np.frombuffer(goal.embedding_vector, dtype=np.float32)
        else:
            goal_emb = embedder.encode([goal.goal_text])[0]
            
        sim = float(cosine_similarity([article_embedding], [goal_emb])[0][0])
        
        match_type = "semantic"
        matched_kw = None
        
        # Keyword Boost
        keywords = extract_keywords(goal.goal_text)
        is_match, kw = keyword_match(article_text, keywords)
        if is_match:
            sim = min(sim + 0.3, 1.0)
            match_type = "keyword"
            matched_kw = kw
            
        if sim > best_score:
            best_score = sim
            best_goal_id = goal.id
            best_match_type = match_type
            best_matched_keyword = matched_kw
            
    return best_score, best_goal_id, best_match_type, best_matched_keyword
