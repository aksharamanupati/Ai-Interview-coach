"""
Session evaluation aggregator and rubric scorecard generator.
"""
import uuid
from datetime import datetime
from typing import List, Dict
from core.models import AnswerEvaluation, SessionSummary
from evaluation.readiness_calculator import calculate_readiness
from evaluation.roadmap_generator import generate_practice_roadmap

def summarize_session(
    candidate_name: str,
    target_role: str,
    interview_mode: str,
    difficulty: str,
    evaluations: List[AnswerEvaluation]
) -> SessionSummary:
    """Summarize an entire practice interview session into a SessionSummary."""
    session_id = f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:6]}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not evaluations:
        return SessionSummary(
            session_id=session_id,
            timestamp=timestamp,
            candidate_name=candidate_name,
            target_role=target_role,
            interview_mode=interview_mode,
            difficulty=difficulty,
            overall_score=0.0,
            readiness_score=0.0,
            readiness_band="Needs Practice",
            readiness_explanation="No answers were recorded during this session.",
            dimension_scores={},
            strongest_answers=[],
            priority_weaknesses=["Incomplete session."],
            top_3_actions=["Start an interview and complete at least 3 questions."],
            recommended_next_focus=["Foundational practice"],
            practice_roadmap=[],
            evaluations=[]
        )

    # 1. Compute Dimension Averages
    dim_totals: Dict[str, float] = {}
    dim_counts: Dict[str, int] = {}
    
    for ev in evaluations:
        for dim_name, d_eval in ev.dimensions.items():
            dim_totals[dim_name] = dim_totals.get(dim_name, 0.0) + d_eval.score
            dim_counts[dim_name] = dim_counts.get(dim_name, 0) + 1

    dimension_scores = {
        dim: round(dim_totals[dim] / dim_counts[dim], 1)
        for dim in dim_totals
    }

    # Overall score across all questions
    overall_score = round(sum(ev.overall_score for ev in evaluations) / len(evaluations), 1)

    # Readiness score & band
    readiness_score, readiness_band, readiness_desc = calculate_readiness(dimension_scores)

    # Sort answers by performance
    sorted_evals = sorted(evaluations, key=lambda e: e.overall_score, reverse=True)
    strongest_answers = [
        f"'{e.question_text[:60]}...' ({e.overall_score}/100) — {e.key_strength}"
        for e in sorted_evals[:2]
    ]

    # Prioritize weaknesses
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])
    priority_weaknesses = [
        f"{dim} ({score}/100)"
        for dim, score in sorted_dims[:3] if score < 80.0
    ]
    if not priority_weaknesses and sorted_dims:
        priority_weaknesses = [f"{sorted_dims[0][0]} ({sorted_dims[0][1]}/100)"]

    # Top 3 improvement actions (actionable and specific)
    top_3_actions = []
    for dim, score in sorted_dims[:3]:
        if dim == "Structure":
            top_3_actions.append("Practice STAR framing: Anchor your answer with a 1-sentence situation, your exact technical task, actions taken, and the measurable result.")
        elif dim == "Technical Depth":
            top_3_actions.append("Explain execution internals: Describe why an algorithm was selected and what memory/time complexity bottlenecks were navigated.")
        elif dim == "Specificity":
            top_3_actions.append("Quantify your project achievements: State concrete dataset counts, percentage efficiency boosts, or profiling benchmarks.")
        elif dim == "Clarity":
            top_3_actions.append("Eliminate verbal fillers: Pause in silence for 2 seconds when organizing thoughts instead of saying 'um' or 'like'.")
        elif dim == "Conciseness":
            top_3_actions.append("Aim for 60-90 second answers: Avoid lengthy introductory preambles and dive directly into the prompt.")
        elif dim == "Relevance":
            top_3_actions.append("Direct prompt alignment: Directly answer the question in your opening sentence before adding background detail.")

    if len(top_3_actions) < 3:
        top_3_actions.append("Practice regular timed mock sessions to build conversational fluency and confidence.")

    # Recommended next session focus areas
    recommended_next_focus = [dim for dim, _ in sorted_dims[:2]]

    # 7-day practice roadmap
    roadmap = generate_practice_roadmap([d for d, _ in sorted_dims[:3]], target_role=target_role)

    return SessionSummary(
        session_id=session_id,
        timestamp=timestamp,
        candidate_name=candidate_name,
        target_role=target_role,
        interview_mode=interview_mode,
        difficulty=difficulty,
        overall_score=overall_score,
        readiness_score=readiness_score,
        readiness_band=readiness_band,
        readiness_explanation=readiness_desc,
        dimension_scores=dimension_scores,
        strongest_answers=strongest_answers,
        priority_weaknesses=priority_weaknesses,
        top_3_actions=top_3_actions[:3],
        recommended_next_focus=recommended_next_focus,
        practice_roadmap=roadmap,
        evaluations=evaluations
    )
