"""Streamlit entry point for AI Interview Coach."""
from ui.interview_app import (
    build_result_cards,
    build_resume_analysis_summary,
    check_repeat_question_safe,
    explain_question_in_language,
    get_stage_progress,
    next_question_after_answer,
    run_app,
)


if __name__ == "__main__":
    run_app()
