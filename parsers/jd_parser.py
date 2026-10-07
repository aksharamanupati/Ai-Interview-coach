"""
Job Description Parser.
Extracts title, required skills, preferred skills, and core responsibilities.
"""
import re
from core.models import JobDescriptionData
from parsers.resume_parser import COMMON_TECH_SKILLS, format_skill_name

def parse_job_description(raw_text: str, default_title: str = "Software Engineer") -> JobDescriptionData:
    """Parse raw job description text into structured JobDescriptionData."""
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    text_lower = raw_text.lower()
    
    # Title extraction heuristic
    title = default_title
    for line in lines[:5]:
        if re.search(r"(engineer|developer|analyst|intern|scientist|architect|specialist)\b", line, re.IGNORECASE):
            # Clean title
            clean_title = re.sub(r"^(?:job title|role|position|opening)\s*[:\-]\s*", "", line, flags=re.IGNORECASE)
            if len(clean_title) < 50:
                title = clean_title.strip()
                break

    # Extract technical skills
    found_skills = []
    for skill in COMMON_TECH_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.append(format_skill_name(skill))

    # Segment required vs preferred skills
    required_skills = []
    preferred_skills = []
    
    in_required = False
    in_preferred = False
    
    for line in lines:
        if re.search(r"(?:requirements|required skills|must have|qualifications|eligibility)", line, re.IGNORECASE):
            in_required = True
            in_preferred = False
            continue
        if re.search(r"(?:preferred|nice to have|plus|bonus|good to have)", line, re.IGNORECASE):
            in_preferred = True
            in_required = False
            continue
            
        line_skills = [s for s in found_skills if re.search(r"\b" + re.escape(s) + r"\b", line, re.IGNORECASE)]
        if in_preferred:
            preferred_skills.extend(line_skills)
        elif in_required or line_skills:
            required_skills.extend(line_skills)

    # Fallback partition if no explicit sections were present
    if not required_skills and not preferred_skills:
        required_skills = found_skills[:max(1, int(len(found_skills) * 0.7))]
        preferred_skills = found_skills[len(required_skills):]
    elif not required_skills and preferred_skills:
        required_skills = preferred_skills
        preferred_skills = []

    # Deduplicate
    def dedup(lst):
        seen = set()
        res = []
        for x in lst:
            if x.lower() not in seen:
                res.append(x)
                seen.add(x.lower())
        return res

    required_skills = dedup(required_skills)
    preferred_skills = [s for s in dedup(preferred_skills) if s.lower() not in [r.lower() for r in required_skills]]

    # Extract Responsibilities
    responsibilities = []
    in_resp = False
    for line in lines:
        if re.search(r"(?:responsibilities|duties|what you will do|role description)", line, re.IGNORECASE):
            in_resp = True
            continue
        if in_resp and any(re.search(rf"^{re.escape(h)}", line, re.IGNORECASE) for h in ["requirements", "skills", "benefits", "about us", "qualifications"]):
            in_resp = False
        if in_resp and line.startswith(("•", "-", "*", "1", "2", "3", "4", "5")):
            responsibilities.append(line.lstrip("•-*0123456789. "))
            if len(responsibilities) >= 6:
                break

    return JobDescriptionData(
        title=title,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        responsibilities=responsibilities,
        raw_text=raw_text
    )
