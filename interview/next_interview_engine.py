"""
Next Interview Adaptation Engine & Multi-Session Comparison.
Implements the Core USP: The interview coach that learns from every session
and automatically targets prior weaknesses in the next interview.
"""
from typing import Dict, Any, List, Optional
from storage.session_db import get_all_sessions

def prepare_next_interview_profile(candidate_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze historical sessions and build a tailored configuration for the next interview.
    """
    sessions = get_all_sessions(candidate_name)
    if not sessions:
        return {
            "has_history": False,
            "session_count": 0,
            "recommended_mode": "Mixed",
            "recommended_difficulty": "Medium",
            "targeted_weaknesses": [],
            "focus_message": "Welcome to your first session! We'll establish your baseline performance across technical, project, and behavioral dimensions."
        }
        
    last_session = sessions[-1]
    weaknesses = last_session.get("priority_weaknesses", [])
    dim_scores = last_session.get("dimension_scores", {})
    
    # Identify lowest scoring dimension
    sorted_dims = sorted(dim_scores.items(), key=lambda x: x[1])
    lowest_dim = sorted_dims[0][0] if sorted_dims else "Technical Depth"
    lowest_score = sorted_dims[0][1] if sorted_dims else 60.0
    
    # Map lowest dimension to recommended mode
    if lowest_dim in ["Structure", "Clarity"]:
        rec_mode = "Behavioral"
    elif lowest_dim in ["Technical Depth", "Specificity"]:
        rec_mode = "Technical"
    else:
        rec_mode = "Project"
        
    # Calibrate difficulty: if last overall was > 85, increase difficulty; if < 60, make it accessible
    last_overall = last_session.get("overall_score", 70.0)
    if last_overall >= 85.0:
        rec_diff = "Hard"
    elif last_overall <= 55.0:
        rec_diff = "Easy"
    else:
        rec_diff = "Medium"

    focus_msg = (
        f"Session #{len(sessions)+1} Adaptation: Prior session highlighted '{lowest_dim}' "
        f"({lowest_score}/100) as your primary growth area. The next session will automatically "
        f"integrate targeted questions to remediate this weakness."
    )

    return {
        "has_history": True,
        "session_count": len(sessions),
        "last_session_id": last_session.get("session_id"),
        "last_overall_score": last_overall,
        "recommended_mode": rec_mode,
        "recommended_difficulty": rec_diff,
        "targeted_weaknesses": weaknesses,
        "primary_focus_dimension": lowest_dim,
        "focus_message": focus_msg
    }

def compare_sessions(candidate_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Compare Session N vs Session N-1 to calculate measurable improvement metrics.
    Satisfies PRD Section 11 & Section 25.
    """
    sessions = get_all_sessions(candidate_name)
    if len(sessions) < 2:
        return {
            "can_compare": False,
            "message": "Complete at least two interview sessions to generate a comparative progress trajectory."
        }
        
    s_prev = sessions[-2]
    s_curr = sessions[-1]
    
    overall_delta = round(s_curr["overall_score"] - s_prev["overall_score"], 1)
    readiness_delta = round(s_curr["readiness_score"] - s_prev["readiness_score"], 1)
    
    dim_deltas = {}
    prev_dims = s_prev.get("dimension_scores", {})
    curr_dims = s_curr.get("dimension_scores", {})
    
    all_dims = set(prev_dims.keys()).union(set(curr_dims.keys()))
    for d in all_dims:
        p_val = prev_dims.get(d, 0.0)
        c_val = curr_dims.get(d, 0.0)
        dim_deltas[d] = {
            "previous": p_val,
            "current": c_val,
            "delta": round(c_val - p_val, 1)
        }

    # Resolved weaknesses check
    prev_weak = set([w.split()[0] for w in s_prev.get("priority_weaknesses", [])])
    curr_weak = set([w.split()[0] for w in s_curr.get("priority_weaknesses", [])])
    resolved = list(prev_weak - curr_weak)

    return {
        "can_compare": True,
        "previous_session_id": s_prev["session_id"],
        "current_session_id": s_curr["session_id"],
        "previous_overall": s_prev["overall_score"],
        "current_overall": s_curr["overall_score"],
        "overall_delta": overall_delta,
        "readiness_delta": readiness_delta,
        "dimension_comparisons": dim_deltas,
        "resolved_weaknesses": resolved,
        "summary": (
            f"Overall practice score changed by {overall_delta:+0.1f} pts ({s_prev['overall_score']} -> {s_curr['overall_score']}). "
            f"Readiness moved by {readiness_delta:+0.1f} pts. "
            f"{f'Resolved prior weakness in {resolved}.' if resolved else 'Continued practice on core competencies.'}"
        )
    }
