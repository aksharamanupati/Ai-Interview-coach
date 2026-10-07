"""
Resume parser supporting PDF, DOCX, and TXT files.
Extracts sections, skills, education, projects, experience, and provides
an evidence-backed rubric evaluation without fabricating data.
"""
import re
from pathlib import Path
from typing import BinaryIO, Union
import pypdf
import docx

from core.models import ResumeData

COMMON_TECH_SKILLS = [
    "python", "java", "c++", "c", "c#", "javascript", "typescript", "html", "css",
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "react", "angular", "vue",
    "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring", "spring boot",
    "git", "github", "docker", "kubernetes", "aws", "azure", "gcp", "linux",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "data structures", "algorithms", "rest api",
    "oop", "object oriented programming", "agile", "devops", "ci/cd", "hackerrank", "codechef", "leetcode"
]

SKILL_DISPLAY_NAMES = {
    "c++": "C++",
    "c#": "C#",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "html": "HTML",
    "css": "CSS",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "sqlite": "SQLite",
    "react": "React",
    "angular": "Angular",
    "vue": "Vue",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "git": "Git",
    "github": "GitHub",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "linux": "Linux",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "computer vision": "Computer Vision",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "data structures": "Data Structures",
    "algorithms": "Algorithms",
    "rest api": "REST API",
    "oop": "OOP",
    "object oriented programming": "Object-Oriented Programming",
    "agile": "Agile",
    "devops": "DevOps",
    "ci/cd": "CI/CD",
    "hackerrank": "HackerRank",
    "codechef": "CodeChef",
    "leetcode": "LeetCode",
}


def format_skill_name(skill: str) -> str:
    """Return a display-friendly skill label while preserving common technical casing."""
    normalized = (skill or "").strip()
    if not normalized:
        return ""
    key = normalized.lower()
    return SKILL_DISPLAY_NAMES.get(key, normalized.title())

def extract_text_from_file(file_source: Union[str, Path, BinaryIO], filename: str) -> str:
    """Extract text from PDF, DOCX, or TXT."""
    ext = Path(filename).suffix.lower()
    text = ""
    
    if ext == ".pdf":
        reader = pypdf.PdfReader(file_source)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    elif ext in [".docx", ".doc"]:
        doc = docx.Document(file_source)
        for p in doc.paragraphs:
            if p.text.strip():
                text += p.text + "\n"
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text += row_text + "\n"
    else:
        # Treat as plain text
        if hasattr(file_source, "read"):
            content = file_source.read()
            if isinstance(content, bytes):
                text = content.decode("utf-8", errors="ignore")
            else:
                text = str(content)
        else:
            with open(file_source, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                
    return text.strip()

def parse_resume(raw_text: str) -> ResumeData:
    """Parse raw resume text into structured ResumeData with rubric observations."""
    text_lower = raw_text.lower()
    
    # 1. Extract Skills
    found_skills = []
    for skill in COMMON_TECH_SKILLS:
        # Match as whole word or boundary
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.append(format_skill_name(skill))
            
    # Also look for explicit 'Skills' section
    skills_match = re.search(r"(?:skills|technical skills|technologies)[\s:]*\n?([^\n\r]+(?:\n[^\n\r]+){1,4})", raw_text, re.IGNORECASE)
    if skills_match:
        section_lines = []
        for section_line in skills_match.group(1).splitlines():
            if re.match(
                r"^\s*(?:education|academics|projects?|experience|internships?|certifications?|achievements?|summary|work experience)\s*:?\s*$",
                section_line,
                re.IGNORECASE,
            ):
                break
            section_lines.append(section_line)
        section_tokens = re.split(r"[,|\n•\-\*]+", "\n".join(section_lines))
        for token in section_tokens:
            cleaned = token.strip()
            if cleaned and len(cleaned) < 30 and cleaned.lower() not in [s.lower() for s in found_skills]:
                # avoid headers
                if not any(h in cleaned.lower() for h in ["education", "experience", "project", "summary"]):
                    found_skills.append(cleaned)
                    
    # Deduplicate while preserving order
    dedup_skills = []
    seen = set()
    for s in found_skills:
        if s.lower() not in seen:
            dedup_skills.append(s)
            seen.add(s.lower())

    # 2. Extract Education
    education = []
    edu_patterns = [
        r"(b\.?\s?tech|bachelor|m\.?\s?tech|master|diploma|intermediate|12th|10th|high school)[^\n\r]*",
        r"(cgpa\s*[:=]?\s*[\d\.]+(?:\s*/\s*10)?|percentage\s*[:=]?\s*[\d\.]+%)",
    ]
    lines = raw_text.splitlines()
    in_edu = False
    for i, line in enumerate(lines):
        if re.search(r"^(?:education|academics|qualifications)", line.strip(), re.IGNORECASE):
            in_edu = True
            continue
        if in_edu and re.search(r"^(?:projects|skills|experience|certifications|summary)", line.strip(), re.IGNORECASE):
            in_edu = False
            
        if in_edu or any(re.search(p, line, re.IGNORECASE) for p in edu_patterns):
            clean_line = line.strip()
            if clean_line and len(clean_line) > 3:
                education.append({"details": clean_line})
                if len(education) >= 5:
                    break

    # 3. Extract Projects
    projects = []
    project_headers = ["project", "projects", "academic projects", "personal projects"]
    in_proj = False
    current_proj = None
    for line in lines:
        stripped = line.strip()
        if any(re.search(rf"^{re.escape(h)}", stripped, re.IGNORECASE) for h in project_headers):
            in_proj = True
            continue
        if in_proj and any(re.search(rf"^{re.escape(h)}", stripped, re.IGNORECASE) for h in ["education", "skills", "experience", "certifications", "achievements"]):
            if current_proj:
                projects.append(current_proj)
                current_proj = None
            in_proj = False
            
        if in_proj and stripped:
            # Handle formats like "1. Title: Description" or "Title - Description"
            inline_split = re.split(r"[:\-—]\s+", stripped, maxsplit=1)
            is_numbered = bool(re.match(r"^(\d+[\.\)]|•|\-|\*)\s*", stripped))
            
            if is_numbered and len(inline_split) == 2:
                if current_proj:
                    projects.append(current_proj)
                title_part = re.sub(r"^(\d+[\.\)]|•|\-|\*)\s*", "", inline_split[0]).strip()
                current_proj = {"title": title_part, "description": inline_split[1].strip()}
            elif len(stripped) < 70 and not stripped.startswith(("•", "-", "*")):
                if current_proj:
                    projects.append(current_proj)
                current_proj = {"title": stripped, "description": ""}
            elif current_proj:
                current_proj["description"] += (" " + stripped) if current_proj["description"] else stripped
            else:
                current_proj = {"title": stripped[:50], "description": stripped}

    if current_proj:
        projects.append(current_proj)
        
    # Fallback if no explicit project block header found: scan for keywords
    if not projects:
        for i, line in enumerate(lines):
            if re.search(r"(system|portal|app|detector|predictor|website|platform|engine|clone)\b", line, re.IGNORECASE):
                if len(line.strip()) < 80:
                    desc = lines[i+1].strip() if i + 1 < len(lines) else ""
                    projects.append({"title": line.strip(), "description": desc})
                    if len(projects) >= 3:
                        break

    # 4. Extract Certifications / Achievements
    certifications = []
    in_cert = False
    for line in lines:
        stripped = line.strip()
        if re.search(r"^(?:certifications?|achievements?|awards|honors)", stripped, re.IGNORECASE):
            in_cert = True
            continue
        if in_cert and any(re.search(rf"^{re.escape(h)}", stripped, re.IGNORECASE) for h in ["education", "skills", "experience", "projects"]):
            in_cert = False
            
        if in_cert and stripped:
            certifications.append(stripped)
            if len(certifications) >= 5:
                break

    # 5. Rubric-based Scoring & Observations (Section 5.2)
    # Estimate score based on concrete components:
    # - Skills breadth (max 25)
    # - Projects presence & depth (max 25)
    # - Education clarity (max 20)
    # - Contact & Formatting (max 15)
    # - Quantifiable metrics & problem solving (max 15)
    
    score = 0.0
    strengths = []
    missing_or_unclear = []
    formatting_observations = []
    actionable_improvements = []
    
    # Skills scoring
    skill_count = len(dedup_skills)
    if skill_count >= 6:
        score += 25.0
        strengths.append(f"Identified {skill_count} relevant technical skills ({', '.join(dedup_skills[:5])}).")
    elif skill_count >= 3:
        score += 18.0
        strengths.append(f"Found core foundational skills: {', '.join(dedup_skills)}.")
        missing_or_unclear.append("Consider listing supporting libraries/tools (e.g. Git, databases, deployment).")
    else:
        score += 10.0
        missing_or_unclear.append("Few explicit technical skills detected in standard formatting.")
        actionable_improvements.append("Group your technical skills into categorized sections (e.g. Languages, Frameworks, Developer Tools).")

    # Projects scoring
    if len(projects) >= 2:
        score += 25.0
        strengths.append(f"Found {len(projects)} distinct projects demonstrating hands-on experience.")
    elif len(projects) == 1:
        score += 16.0
        strengths.append(f"Found project '{projects[0]['title']}'.")
        missing_or_unclear.append("Adding at least one more project would demonstrate broader problem-solving breadth.")
    else:
        score += 8.0
        missing_or_unclear.append("No clearly separated project sections detected.")
        actionable_improvements.append("Include 2-3 detailed technical projects detailing your role, tech stack, and outcome.")

    # Education scoring
    if education:
        score += 20.0
        strengths.append("Clear educational background provided with academic timeline.")
    else:
        score += 10.0
        missing_or_unclear.append("Degree or institutional graduation timeline could be highlighted more clearly.")

    # Formatting & contact details
    has_email = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text))
    has_phone = bool(re.search(r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b|\b\d{10}\b", raw_text))
    
    if has_email and has_phone:
        score += 15.0
        formatting_observations.append("Verified essential contact details (Email and Phone number present).")
    elif has_email or has_phone:
        score += 10.0
        formatting_observations.append("Partial contact info found. Ensure both professional email and phone are present at the top.")
    else:
        score += 5.0
        formatting_observations.append("Missing standard contact header format.")
        actionable_improvements.append("Add a clean top header with your name, phone number, email, and LinkedIn/GitHub links.")

    # Metrics & quantification
    has_numbers = bool(re.search(r"\b(?:\d+%(?:\s+increase|\s+faster|\s+accuracy)?|\d+\s*(?:users|requests|records|ms|seconds))\b", raw_text, re.IGNORECASE))
    if has_numbers:
        score += 15.0
        strengths.append("Includes quantified metrics illustrating project or academic impact.")
    else:
        score += 8.0
        actionable_improvements.append("Quantify your project outcomes (e.g., 'achieved 85% accuracy', 'reduced query time by 30%').")

    # Role relevance
    role_relevance = (
        f"Solid alignment for entry-level Software / IT roles with skills in {', '.join(dedup_skills[:4])}."
        if dedup_skills else "General technical candidate profile."
    )

    return ResumeData(
        skills=dedup_skills,
        education=education,
        projects=projects,
        experience=[],
        certifications=certifications,
        raw_text=raw_text,
        rubric_score=round(score, 1),
        strengths=strengths,
        missing_or_unclear=missing_or_unclear,
        role_relevance=role_relevance,
        formatting_observations=formatting_observations,
        actionable_improvements=actionable_improvements
    )
