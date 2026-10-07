"""
Comprehensive Final Interview Report Exporter.
Generates structured Markdown and HTML reports suitable for printing or downloading.
"""
from typing import Optional
from core.models import ResumeData, JobMatchResult, SessionSummary

def generate_markdown_report(
    summary: SessionSummary,
    resume: Optional[ResumeData] = None,
    job_match: Optional[JobMatchResult] = None
) -> str:
    """Generate complete markdown audit report."""
    md = []
    md.append(f"# 🎓 AI Interview Coach — Performance & Coaching Report")
    md.append(f"**Candidate:** {summary.candidate_name} | **Role:** {summary.target_role}")
    md.append(f"**Session Date:** {summary.timestamp} | **Session ID:** `{summary.session_id}`")
    md.append(f"**Interview Mode:** {summary.interview_mode} ({summary.difficulty} Difficulty)\n")
    md.append("---")
    
    # 1. Executive Summary & Readiness
    md.append("## 1. Executive Summary & Practice Readiness")
    md.append(f"- **Overall Practice Score:** **{summary.overall_score} / 100**")
    md.append(f"- **Practice Readiness Status:** **{summary.readiness_band} ({summary.readiness_score}/100)**")
    md.append(f"> ℹ️ *{summary.readiness_explanation}*\n")

    # 2. Rubric Dimension Breakdown
    md.append("## 2. Rubric Dimension Breakdown")
    md.append("| Dimension | Score | Rubric Band |")
    md.append("| :--- | :--- | :--- |")
    for dim, score in summary.dimension_scores.items():
        band_name = "Strong" if score >= 75 else ("Developing" if score >= 60 else "Needs Improvement")
        md.append(f"| {dim} | **{score}/100** | {band_name} |")
    md.append("")

    # 3. Resume & Job Alignment (if provided)
    if resume:
        md.append("## 3. Resume Audit & Observations")
        md.append(f"- **Estimated Resume Health Score:** **{resume.rubric_score}/100**")
        md.append(f"- **Identified Technical Skills:** {', '.join(resume.skills)}")
        if resume.strengths:
            md.append("### Strengths:")
            for s in resume.strengths:
                md.append(f"  - ✅ {s}")
        if resume.actionable_improvements:
            md.append("### Resume Improvements:")
            for imp in resume.actionable_improvements:
                md.append(f"  - 💡 {imp}")
        md.append("")

    if job_match:
        md.append("## 4. Job Description Coverage Matrix")
        md.append(f"- **Match Alignment Score:** **{job_match.match_score}%**")
        md.append(f"- **Summary:** {job_match.summary}")
        md.append("| Target Skill | Coverage Status | Evidence from Resume | Verification Question |")
        md.append("| :--- | :--- | :--- | :--- |")
        for item in job_match.coverage_items:
            md.append(f"| {item.skill} | **{item.status}** | {item.resume_evidence} | {item.verification_question} |")
        md.append("")

    # 5. Question-by-Question Coaching & Verbatim Evidence
    md.append("## 5. Question-Level Feedback & Evidence")
    for idx, ev in enumerate(summary.evaluations, start=1):
        md.append(f"### Question {idx}: {ev.question_text}")
        md.append(f"- **Score:** **{ev.overall_score}/100**")
        if ev.was_edited:
            md.append(f"- *Note: Candidate verified and edited transcription prior to evaluation.*")
        md.append(f"- **Candidate Answer:** *\"{ev.edited_transcript}\"*")
        md.append(f"- **Primary Strength:** {ev.key_strength}")
        md.append(f"- **Key Area for Growth:** {ev.priority_weakness}")
        
        md.append("\n**Dimension Details:**")
        for d_name, d_obj in ev.dimensions.items():
            quotes = f" (Evidence: *\"{d_obj.evidence_quotes[0]}\"*)" if d_obj.evidence_quotes else ""
            md.append(f"- **{d_name} ({d_obj.score}/100):** {d_obj.rationale}{quotes} ➔ *Fix: {d_obj.actionable_improvement}*")
            
        md.append("\n**✨ Improve My Answer (STAR Format Preserving Real Experience):**")
        md.append(f"> {ev.star_version}\n")

    # 6. Top 3 Next Actions & 7-Day Roadmap
    md.append("## 6. Actionable Next Steps & 7-Day Roadmap")
    for idx, act in enumerate(summary.top_3_actions, start=1):
        md.append(f"{idx}. **{act}**")
    md.append("")
    
    if summary.practice_roadmap:
        md.append("### Personalized 7-Day Practice Plan:")
        md.append("| Day | Topic | Recommended Exercise | Success Metric |")
        md.append("| :--- | :--- | :--- | :--- |")
        for day in summary.practice_roadmap:
            md.append(f"| {day['day']} | **{day['topic']}** | {day['activity']} | {day['target_metric']} |")
        md.append("")

    md.append("---")
    md.append("### 🛡️ Ethical & Fairness Commitment")
    md.append("*AI Interview Coach scores are strictly calibrated practice metrics designed to accelerate candidate growth. They do not represent employment decisions, hiring predictions, or personality evaluations.*")

    return "\n".join(md)
