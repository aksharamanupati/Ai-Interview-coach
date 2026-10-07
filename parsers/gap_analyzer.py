"""
JD vs Resume Gap Analyzer and Coverage Matrix.
Maps candidate resume against target job description requirements,
computes match score, and generates verification questions.
"""
import re
from core.models import ResumeData, JobDescriptionData, CoverageItem, JobMatchResult

# Related skill clusters for detecting partial matches
SKILL_CLUSTERS = {
    "python": ["django", "flask", "fastapi", "pandas", "numpy", "pytorch"],
    "javascript": ["typescript", "react", "node.js", "nodejs", "express", "html", "css"],
    "java": ["spring", "spring boot", "oop"],
    "c++": ["c", "algorithms", "data structures", "oop"],
    "sql": ["mysql", "postgresql", "mongodb", "sqlite", "database"],
    "docker": ["kubernetes", "devops", "ci/cd", "linux"],
    "aws": ["azure", "gcp", "cloud", "docker"],
    "machine learning": ["deep learning", "nlp", "computer vision", "scikit-learn", "tensorflow", "pytorch"],
}

def analyze_gap(resume: ResumeData, jd: JobDescriptionData) -> JobMatchResult:
    """Compare resume against job description and construct coverage matrix."""
    resume_skills_lower = {s.lower(): s for s in resume.skills}
    resume_text_lower = resume.raw_text.lower()
    
    all_target_skills = jd.required_skills + jd.preferred_skills
    if not all_target_skills:
        all_target_skills = ["Python", "Data Structures", "Algorithms", "Git", "SQL"]

    coverage_items: list[CoverageItem] = []
    matched = []
    missing = []
    score_points = 0.0
    total_weights = 0.0

    for skill in all_target_skills:
        s_low = skill.lower()
        is_required = skill in jd.required_skills
        weight = 2.0 if is_required else 1.0
        total_weights += weight
        
        # 1. Check direct match
        if s_low in resume_skills_lower or re.search(r"\b" + re.escape(s_low) + r"\b", resume_text_lower):
            # Find evidence
            evidence = f"Explicitly listed under candidate skills/resume text."
            # Check if mentioned in a project
            for p in resume.projects:
                if s_low in p.get("title", "").lower() or s_low in p.get("description", "").lower():
                    evidence = f"Applied in project '{p['title']}'."
                    break
                    
            coverage_items.append(CoverageItem(
                skill=skill,
                status="Strong Match",
                resume_evidence=evidence,
                confidence=0.95,
                verification_question=f"How did you implement {skill} in your projects, and what architectural tradeoffs did you make?"
            ))
            matched.append(skill)
            score_points += weight
            
        else:
            # 2. Check cluster / related skill partial match
            related_found = []
            for cluster_key, related_list in SKILL_CLUSTERS.items():
                if s_low == cluster_key or s_low in related_list:
                    for rel in [cluster_key] + related_list:
                        if rel in resume_skills_lower:
                            related_found.append(resume_skills_lower[rel])
            
            if related_found:
                rel_str = ", ".join(list(set(related_found))[:3])
                coverage_items.append(CoverageItem(
                    skill=skill,
                    status="Partial Match",
                    resume_evidence=f"Demonstrated foundational background via related competency: {rel_str}.",
                    confidence=0.65,
                    verification_question=f"Given your experience in {rel_str}, how quickly could you transfer those concepts to working with {skill}?"
                ))
                matched.append(f"{skill} (via {rel_str})")
                score_points += (weight * 0.6)
            else:
                # 3. Missing Evidence
                coverage_items.append(CoverageItem(
                    skill=skill,
                    status="Missing Evidence",
                    resume_evidence="Not explicitly referenced in the current resume version.",
                    confidence=0.30,
                    verification_question=f"Have you worked with {skill} outside your listed projects, or how would you approach learning it for this role?"
                ))
                missing.append(skill)

    overall_match = round((score_points / total_weights) * 100.0, 1) if total_weights > 0 else 70.0
    
    summary = (
        f"Match Score: {overall_match}%. Found strong/partial alignment for {len(matched)} target skills. "
        f"{len(missing)} requirements not yet evidenced in resume."
    )

    return JobMatchResult(
        match_score=overall_match,
        coverage_items=coverage_items,
        matched_skills=matched,
        missing_skills=missing,
        summary=summary
    )
