"""
Data schemas and domain models for AI Interview Coach.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class ResumeData:
    skills: List[str] = field(default_factory=list)
    education: List[Dict[str, str]] = field(default_factory=list)
    projects: List[Dict[str, str]] = field(default_factory=list)
    experience: List[Dict[str, str]] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    raw_text: str = ""
    rubric_score: float = 75.0
    strengths: List[str] = field(default_factory=list)
    missing_or_unclear: List[str] = field(default_factory=list)
    role_relevance: str = ""
    formatting_observations: List[str] = field(default_factory=list)
    actionable_improvements: List[str] = field(default_factory=list)

@dataclass
class JobDescriptionData:
    title: str = "Software Engineer"
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    raw_text: str = ""

@dataclass
class CoverageItem:
    skill: str
    status: str  # "Strong Match", "Partial Match", "Missing Evidence"
    resume_evidence: str
    confidence: float
    verification_question: str

@dataclass
class JobMatchResult:
    match_score: float = 0.0
    coverage_items: List[CoverageItem] = field(default_factory=list)
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    summary: str = ""

@dataclass
class Question:
    id: str
    text: str
    mode: str  # HR, Technical, Behavioral, Project, Mixed, Campus Placement
    difficulty: str  # Easy, Medium, Hard
    provenance: str  # Why selected: Resume evidence + JD gap + Prior weakness
    target_dimension: str = "Technical Depth"
    is_followup: bool = False
    parent_question_id: Optional[str] = None
    suggested_criteria: List[str] = field(default_factory=list)

@dataclass
class DimensionEvaluation:
    dimension: str
    score: float
    band: str
    rationale: str
    evidence_quotes: List[str]
    actionable_improvement: str

@dataclass
class AnswerEvaluation:
    question_id: str
    question_text: str
    raw_transcript: str
    edited_transcript: str
    was_edited: bool
    overall_score: float
    dimensions: Dict[str, DimensionEvaluation]
    priority_weakness: str
    key_strength: str
    improved_answer: str
    star_version: str
    followup_question: Optional[Question] = None

@dataclass
class SessionSummary:
    session_id: str
    timestamp: str
    candidate_name: str
    target_role: str
    interview_mode: str
    difficulty: str
    overall_score: float
    readiness_score: float
    readiness_band: str
    readiness_explanation: str
    dimension_scores: Dict[str, float]
    strongest_answers: List[str]
    priority_weaknesses: List[str]
    top_3_actions: List[str]
    recommended_next_focus: List[str]
    practice_roadmap: List[Dict[str, Any]]
    evaluations: List[AnswerEvaluation]
