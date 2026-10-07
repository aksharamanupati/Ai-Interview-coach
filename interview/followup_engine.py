"""
Adaptive Follow-Up Engine.
Probes vague answers, verifies resume claims, and evaluates technical depth dynamically.
"""
from typing import Optional
from core.models import Question, ResumeData
from ai_providers import get_ai_provider

def generate_adaptive_followup(
    question: Question,
    answer_text: str,
    resume: ResumeData,
    provider_name: str = "offline",
    api_key: str = ""
) -> Optional[Question]:
    """Dynamically determine whether an adaptive follow-up question is warranted."""
    provider = get_ai_provider(provider_name, api_key=api_key)
    return provider.generate_followup(question, answer_text, resume)
