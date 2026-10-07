"""
Abstract base class for AI Providers (pluggable architecture).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from core.models import ResumeData, JobDescriptionData, Question, AnswerEvaluation

class BaseAIProvider(ABC):
    
    @abstractmethod
    def generate_questions(
        self,
        resume: ResumeData,
        jd: Optional[JobDescriptionData],
        mode: str,
        difficulty: str,
        count: int = 5,
        previous_weaknesses: Optional[List[str]] = None
    ) -> List[Question]:
        """Generate personalized questions grounded in resume, JD, and past weaknesses."""
        pass

    @abstractmethod
    def generate_followup(
        self,
        question: Question,
        answer_text: str,
        resume: ResumeData
    ) -> Optional[Question]:
        """Generate an adaptive follow-up probing vague or incomplete areas."""
        pass

    @abstractmethod
    def evaluate_answer(
        self,
        question: Question,
        answer_text: str,
        raw_transcript: str,
        resume: ResumeData,
        jd: Optional[JobDescriptionData] = None
    ) -> AnswerEvaluation:
        """Evaluate an answer across defined rubric dimensions with verbatim evidence."""
        pass

    @abstractmethod
    def improve_answer(
        self,
        question: Question,
        answer_text: str,
        weakness_notes: str,
        resume: ResumeData
    ) -> tuple[str, str]:
        """Generate improved and STAR answer versions preserving candidate facts."""
        pass
