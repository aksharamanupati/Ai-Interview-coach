"""
SQLite session database and progress persistence.
Stores session summaries, dimension trajectories, weaknesses, and evaluations.
Enables Session N vs N+1 comparison, weakness-targeted Next Interview generation,
and one-click privacy data deletion.
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from config import DB_PATH
from core.models import SessionSummary, AnswerEvaluation, DimensionEvaluation

def init_db():
    """Initialize database tables."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                timestamp TEXT,
                candidate_name TEXT,
                target_role TEXT,
                interview_mode TEXT,
                difficulty TEXT,
                overall_score REAL,
                readiness_score REAL,
                readiness_band TEXT,
                readiness_explanation TEXT,
                dimension_scores TEXT,
                strongest_answers TEXT,
                priority_weaknesses TEXT,
                top_3_actions TEXT,
                recommended_next_focus TEXT,
                practice_roadmap TEXT,
                evaluations_json TEXT
            )
        """)
        conn.commit()

# Run init immediately
init_db()

def save_session(summary: SessionSummary) -> bool:
    """Save a session summary into SQLite."""
    try:
        # Serialize evaluations to JSON
        evals_data = []
        for e in summary.evaluations:
            dims = {
                d_name: {
                    "dimension": d.dimension,
                    "score": d.score,
                    "band": d.band,
                    "rationale": d.rationale,
                    "evidence_quotes": d.evidence_quotes,
                    "actionable_improvement": d.actionable_improvement
                }
                for d_name, d in e.dimensions.items()
            }
            evals_data.append({
                "question_id": e.question_id,
                "question_text": e.question_text,
                "raw_transcript": e.raw_transcript,
                "edited_transcript": e.edited_transcript,
                "was_edited": e.was_edited,
                "overall_score": e.overall_score,
                "dimensions": dims,
                "priority_weakness": e.priority_weakness,
                "key_strength": e.key_strength,
                "improved_answer": e.improved_answer,
                "star_version": e.star_version
            })

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                summary.session_id,
                summary.timestamp,
                summary.candidate_name,
                summary.target_role,
                summary.interview_mode,
                summary.difficulty,
                summary.overall_score,
                summary.readiness_score,
                summary.readiness_band,
                summary.readiness_explanation,
                json.dumps(summary.dimension_scores),
                json.dumps(summary.strongest_answers),
                json.dumps(summary.priority_weaknesses),
                json.dumps(summary.top_3_actions),
                json.dumps(summary.recommended_next_focus),
                json.dumps(summary.practice_roadmap),
                json.dumps(evals_data)
            ))
            conn.commit()
        return True
    except Exception as ex:
        print(f"Error saving session: {ex}")
        return False

def get_all_sessions(candidate_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all historical sessions ordered by timestamp ascending."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if candidate_name:
            cursor.execute("SELECT * FROM sessions WHERE candidate_name = ? ORDER BY timestamp ASC", (candidate_name,))
        else:
            cursor.execute("SELECT * FROM sessions ORDER BY timestamp ASC")
            
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append({
                "session_id": r["session_id"],
                "timestamp": r["timestamp"],
                "candidate_name": r["candidate_name"],
                "target_role": r["target_role"],
                "interview_mode": r["interview_mode"],
                "difficulty": r["difficulty"],
                "overall_score": r["overall_score"],
                "readiness_score": r["readiness_score"],
                "readiness_band": r["readiness_band"],
                "readiness_explanation": r["readiness_explanation"],
                "dimension_scores": json.loads(r["dimension_scores"]),
                "strongest_answers": json.loads(r["strongest_answers"]),
                "priority_weaknesses": json.loads(r["priority_weaknesses"]),
                "top_3_actions": json.loads(r["top_3_actions"]),
                "recommended_next_focus": json.loads(r["recommended_next_focus"]),
                "practice_roadmap": json.loads(r["practice_roadmap"]),
                "evaluations": json.loads(r["evaluations_json"])
            })
        return results

def get_latest_weaknesses(candidate_name: Optional[str] = None) -> List[str]:
    """Retrieve the priority weaknesses from the candidate's most recent session."""
    sessions = get_all_sessions(candidate_name)
    if not sessions:
        return []
    latest = sessions[-1]
    return latest.get("priority_weaknesses", [])

def delete_all_history(candidate_name: Optional[str] = None) -> bool:
    """Clear candidate history as required by Privacy/GDPR controls."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if candidate_name:
            cursor.execute("DELETE FROM sessions WHERE candidate_name = ?", (candidate_name,))
        else:
            cursor.execute("DELETE FROM sessions")
        conn.commit()
    return True
