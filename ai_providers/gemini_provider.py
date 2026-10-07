"""
Google Gemini AI Provider with automatic fallback to Offline provider.
Uses google.generativeai for LLM reasoning when API key is configured.
"""
import re
import json
import logging
from typing import List, Optional
from core.models import ResumeData, JobDescriptionData, Question, AnswerEvaluation
from ai_providers.offline_provider import OfflineAIProvider
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

class GeminiAIProvider:
    def __init__(self, api_key: str = GEMINI_API_KEY, model_name: str = GEMINI_MODEL):
        self.api_key = api_key
        self.model_name = model_name
        self.fallback = OfflineAIProvider()
        self.client = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}. Falling back to offline provider.")
                self.client = None

    def generate_questions(
        self,
        resume: ResumeData,
        jd: Optional[JobDescriptionData],
        mode: str,
        difficulty: str,
        count: int = 5,
        previous_weaknesses: Optional[List[str]] = None
    ) -> List[Question]:
        if not self.client:
            return self.fallback.generate_questions(resume, jd, mode, difficulty, count, previous_weaknesses)
            
        try:
            prompt = (
                f"You are an expert interviewer conducting a {mode} interview ({difficulty} difficulty).\n"
                f"Candidate Skills: {', '.join(resume.skills)}\n"
                f"Candidate Projects: {json.dumps(resume.projects)}\n"
                f"Job Requirements: {', '.join(jd.required_skills) if jd else 'N/A'}\n"
                f"Previous Weaknesses to remediate: {', '.join(previous_weaknesses) if previous_weaknesses else 'None'}\n"
                f"Generate {count} distinct interview questions.\n"
                f"For each question, output JSON list of objects with fields:\n"
                f"id, text, mode, difficulty, provenance, target_dimension, suggested_criteria\n"
                f"Strict rule: Ground questions strictly in their actual projects and skills. Do not invent fake background."
            )
            resp = self.client.generate_content(prompt)
            # Parse or fallback
            text = resp.text.strip()
            # If JSON parse succeeds:
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                items = json.loads(match.group(0))
                qs = []
                for it in items:
                    qs.append(Question(
                        id=str(it.get("id", "q" + str(len(qs)))),
                        text=it.get("text", ""),
                        mode=it.get("mode", mode),
                        difficulty=it.get("difficulty", difficulty),
                        provenance=it.get("provenance", "Generated via Gemini"),
                        target_dimension=it.get("target_dimension", "Technical Depth"),
                        suggested_criteria=it.get("suggested_criteria", [])
                    ))
                if qs:
                    return qs[:count]
        except Exception as e:
            logger.warning(f"Gemini question generation error: {e}. Falling back to offline.")
            
        return self.fallback.generate_questions(resume, jd, mode, difficulty, count, previous_weaknesses)

    def generate_followup(
        self,
        question: Question,
        answer_text: str,
        resume: ResumeData
    ) -> Optional[Question]:
        return self.fallback.generate_followup(question, answer_text, resume)

    def evaluate_answer(
        self,
        question: Question,
        answer_text: str,
        raw_transcript: str,
        resume: ResumeData,
        jd: Optional[JobDescriptionData] = None
    ) -> AnswerEvaluation:
        # Offline provider produces calibrated rubric with guaranteed verbatim quotes
        return self.fallback.evaluate_answer(question, answer_text, raw_transcript, resume, jd)

    def improve_answer(
        self,
        question: Question,
        answer_text: str,
        weakness_notes: str,
        resume: ResumeData
    ) -> tuple[str, str]:
        return self.fallback.improve_answer(question, answer_text, weakness_notes, resume)
