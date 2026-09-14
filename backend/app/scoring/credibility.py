import re
import json
from app.models import Article, Source

# Basic clickbait indicators
CLICKBAIT_PATTERNS = [
    r"\b(will blow your mind|shocking|you won't believe|what happens next|this is why)\b",
    r"\b(one trick|secret to|lifehack)\b",
    r"\b(number \d+ will)\b",
]

def score_credibility(article: Article, source: Source) -> tuple[float, str]:
    reasons = []
    
    # 1. Base trust tier
    is_dynamic = source.category == "Dynamic"
    
    # Penalized baseline for unknown sources from dynamic search
    base_score = 0.3 if is_dynamic else source.base_credibility_score
    current_score = base_score
    reasons.append(f"Base source score ({source.name}): {base_score:.2f}" + (" [Penalized - Unknown Source]" if is_dynamic else ""))
    
    # 2. Headline tactic detection
    title_lower = article.title.lower()
    
    # All caps detection (excluding common acronyms)
    words = article.title.split()
    all_caps_words = [w for w in words if w.isupper() and len(w) > 3]
    if len(all_caps_words) >= 2:
        current_score -= 0.15
        reasons.append("Headline contains excessive ALL CAPS (-0.15)")
        
    # Excessive punctuation
    if title_lower.count("!") > 1 or title_lower.count("?") > 1 or "!?" in title_lower:
        current_score -= 0.1
        reasons.append("Headline contains excessive punctuation (-0.10)")
        
    # Clickbait phrases
    for pattern in CLICKBAIT_PATTERNS:
        if re.search(pattern, title_lower):
            current_score -= 0.2
            reasons.append(f"Headline contains clickbait pattern (-0.20)")
            break
            
    # 3. Sourcing density (heuristics based on quotes and links)
    raw_text = article.raw_text
    
    # Simple quote count
    quote_count = raw_text.count('"') / 2
    if quote_count > 3:
        current_score += 0.05
        reasons.append("Good sourcing density (multiple quotes) (+0.05)")
    elif quote_count == 0 and len(raw_text) > 500:
        current_score -= 0.05
        reasons.append("Low sourcing density (no quotes) (-0.05)")
        
    # Bound the score between 0 and 1
    final_score = max(0.0, min(1.0, current_score))
    
    return final_score, json.dumps(reasons)
