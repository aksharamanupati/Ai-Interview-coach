"""
Interview Readiness Indicator.
Computes a practice-progress readiness score based on transparent rubric dimensions.
Explicitly avoids false precision and never predicts hiring outcomes.
"""
from typing import Dict
from config import get_band_for_score

def calculate_readiness(dimension_scores: Dict[str, float]) -> tuple[float, str, str]:
    """
    Calculate (readiness_score, readiness_band, readiness_explanation).
    """
    if not dimension_scores:
        return 50.0, "Developing", "Initial practice session. Complete more questions for a fuller evaluation."
        
    weights = {
        "Relevance": 0.20,
        "Clarity": 0.15,
        "Structure": 0.20,
        "Specificity": 0.15,
        "Technical Depth": 0.20,
        "Conciseness": 0.10,
    }
    
    total_score = 0.0
    for dim, score in dimension_scores.items():
        w = weights.get(dim, 1.0 / len(dimension_scores))
        total_score += score * w
        
    final_score = round(total_score, 1)
    band_name, band_desc = get_band_for_score(final_score)
    
    # Transparent breakdown explanation
    explanation = (
        f"Practice readiness: {band_name} ({final_score}/100). {band_desc} "
        f"This indicator is designed for practice guidance and self-improvement tracking only; "
        f"it is not a prediction of hiring or employment decisions."
    )
    
    return final_score, band_name, explanation
