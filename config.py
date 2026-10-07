"""
Configuration settings, constants, rubrics, and environment helpers
for the AI Interview Coach platform.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "interview_coach.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment
load_dotenv(BASE_DIR / ".env")

# Provider settings
DEFAULT_PROVIDER = os.getenv("AI_PROVIDER", "offline")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Scoring Rubric constants as per PRD Section 5.10
RUBRIC_DIMENSIONS = [
    "Relevance",
    "Clarity",
    "Structure",
    "Specificity",
    "Technical Depth",
    "Conciseness"
]

RUBRIC_BANDS = [
    (90, 100, "Excellent", "Demonstrates deep mastery, structured examples, and direct answers."),
    (75, 89, "Strong", "Clear and relevant with good evidence; minor polish required."),
    (60, 74, "Developing", "Solid foundational attempt; needs more concrete details and structure."),
    (40, 59, "Needs Improvement", "Vague, incomplete, or rambling; lacks specific evidence or STAR structure."),
    (0, 39, "Major Gap", "Off-topic, non-responsive, or lacks foundational understanding.")
]

def get_band_for_score(score: float) -> tuple[str, str]:
    """Return (Band Name, Description) for a given score (0-100)."""
    score = max(0.0, min(100.0, score))
    for low, high, name, desc in RUBRIC_BANDS:
        if low <= score <= high:
            return name, desc
    return "Developing", "Solid foundational attempt."

def mask_secret(secret: str | None) -> str:
    """Mask sensitive API keys for safe display in UI/logs."""
    if not secret:
        return "Not Set"
    if len(secret) <= 8:
        return "***"
    return f"{secret[:4]}...{secret[-4:]}"
