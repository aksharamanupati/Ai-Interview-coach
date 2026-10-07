"""
Interview Question Generation Engine.
Coordinates question generation with provenance tracking.
"""
from typing import List, Optional
from core.models import ResumeData, JobDescriptionData, Question
from ai_providers import get_ai_provider

def generate_interview_plan(
    resume: ResumeData,
    jd: Optional[JobDescriptionData],
    mode: str = "Mixed",
    difficulty: str = "Medium",
    count: int = 5,
    previous_weaknesses: Optional[List[str]] = None,
    provider_name: str = "offline",
    api_key: str = ""
) -> List[Question]:
    """Generate interview questions with explicit provenance."""
    provider = get_ai_provider(provider_name, api_key=api_key)
    return provider.generate_questions(
        resume=resume,
        jd=jd,
        mode=mode,
        difficulty=difficulty,
        count=count,
        previous_weaknesses=previous_weaknesses
    )
