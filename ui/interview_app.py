"""Premium Streamlit UI for the AI Interview Coach practice flow."""
import base64
import binascii
import html
import io
import time
from pathlib import Path
import wave

import streamlit as st
import streamlit.components.v1 as components
import av

from ai_providers import get_ai_provider
from audio.speech_handler import transcribe_audio_bytes
from config import DEFAULT_PROVIDER, GEMINI_API_KEY
from core.models import Question
from evaluation.rubric_scorer import summarize_session
from parsers.resume_parser import extract_text_from_file, parse_resume
from storage.session_db import delete_all_history, save_session
from ui.report_exporter import generate_markdown_report

interview_media = components.declare_component(
    "interview_media",
    path=str(Path(__file__).parent / "interview_media"),
)


LANGUAGES = [
    ("English", "English"),
    ("తెలుగు", "Telugu"),
    ("हिन्दी", "Hindi"),
    ("தமிழ்", "Tamil"),
    ("ಕನ್ನಡ", "Kannada"),
    ("മലയാളം", "Malayalam"),
    ("मराठी", "Marathi"),
    ("বাংলা", "Bengali"),
]
LANGUAGE_TAGS = {
    "English": "en-IN",
    "Telugu": "te-IN",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN",
    "Bengali": "bn-IN",
}
ROLE_OPTIONS = [
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Data Analyst",
    "Data Scientist",
    "Product Manager",
    "UI/UX Designer",
]
STAGES = ["home", "analysis", "interview", "complete", "feedback", "report"]
STAGE_LABELS = {
    "home": "Resume",
    "analysis": "Analysis",
    "interview": "Interview",
    "complete": "Complete",
    "feedback": "Feedback",
    "report": "Report",
}
RESULT_CATEGORY_ORDER = [
    "Communication",
    "Answer Quality",
    "Technical Knowledge",
    "Confidence / Presentation",
    "Answer Delivery",
]
SAMPLE_RESUME = (
    "Sample Candidate\n"
    "B.Tech Computer Science\n"
    "Technical Skills: Python, React, JavaScript, SQL, Git, Data Structures, Algorithms\n"
    "Projects:\n"
    "1. Emotion-Aware Conversational AI: Built a Python chatbot using REST APIs with 92% classification accuracy.\n"
    "2. Library Management System: Created a relational database application using Python and SQLite for 5000 books.\n"
    "Education: B.Tech Computer Science\n"
)
QUESTION_BANK = [
    {
        "id": "question-01",
        "category": "Introduction",
        "text": "Tell me about yourself and your experience.",
        "telugu": "మీ గురించి మరియు మీ అనుభవం గురించి చెప్పండి.",
        "hindi": "अपने बारे में और अपने अनुभव के बारे में बताइए।",
    },
    {
        "id": "question-02",
        "category": "Projects",
        "text": "Walk me through a project you are proud of and the part you contributed.",
        "telugu": "మీరు గర్వపడే ఒక ప్రాజెక్ట్ గురించి, అందులో మీరు చేసిన కృషి గురించి వివరించండి.",
        "hindi": "अपने उस प्रोजेक्ट के बारे में बताइए जिस पर आपको गर्व है और उसमें आपके योगदान के बारे में समझाइए।",
    },
    {
        "id": "question-03",
        "category": "Problem Solving",
        "text": "What was a difficult technical problem you solved, and how did you approach it?",
        "telugu": "మీరు పరిష్కరించిన ఒక కఠినమైన సాంకేతిక సమస్య ఏమిటి? దాన్ని ఎలా పరిష్కరించారు?",
        "hindi": "आपने कौन-सी कठिन तकनीकी समस्या हल की और उसे हल करने के लिए क्या तरीका अपनाया?",
    },
    {
        "id": "question-04",
        "category": "Role Motivation",
        "text": "Why are you interested in this role and this kind of work?",
        "telugu": "ఈ పాత్రపై మరియు ఈ తరహా పనిపై మీకు ఆసక్తి ఎందుకు?",
        "hindi": "आप इस भूमिका और इस तरह के काम में रुचि क्यों रखते हैं?",
    },
    {
        "id": "question-05",
        "category": "Behavioral",
        "text": "Tell me about a time you handled a challenging situation with a teammate.",
        "telugu": "సహచరుడితో కలిసి ఒక సవాలుతో కూడిన పరిస్థితిని ఎదుర్కొన్న సందర్భం గురించి చెప్పండి.",
        "hindi": "किसी टीम सदस्य के साथ चुनौतीपूर्ण स्थिति को संभालने के अपने अनुभव के बारे में बताइए।",
    },
    {
        "id": "question-06",
        "category": "Technical",
        "text": "Which technical skill are you strongest in, and how have you applied it?",
        "telugu": "మీకు బాగా వచ్చిన సాంకేతిక నైపుణ్యం ఏది? దాన్ని ఎలా ఉపయోగించారు?",
        "hindi": "आपकी सबसे मजबूत तकनीकी कौशल कौन-सी है और आपने उसे कैसे इस्तेमाल किया है?",
    },
    {
        "id": "question-07",
        "category": "Problem Solving",
        "text": "How do you approach debugging an issue you have not seen before?",
        "telugu": "ఇంతకు ముందు చూడని సమస్యను డీబగ్ చేయడానికి మీరు ఎలా ముందుకు వెళ్తారు?",
        "hindi": "किसी अनजान समस्या को डीबग करने के लिए आप किस तरह आगे बढ़ते हैं?",
    },
    {
        "id": "question-08",
        "category": "Learning",
        "text": "Tell me about a mistake or setback and what you learned from it.",
        "telugu": "మీరు చేసిన ఒక పొరపాటు లేదా ఎదురైన అడ్డంకి గురించి, దాని నుంచి నేర్చుకున్నది ఏమిటో చెప్పండి.",
        "hindi": "अपनी किसी गलती या असफलता के बारे में बताइए और आपने उससे क्या सीखा।",
    },
    {
        "id": "question-09",
        "category": "Growth",
        "text": "What skills would you like to develop over the next few years?",
        "telugu": "రాబోయే కొన్ని సంవత్సరాల్లో మీరు ఏ నైపుణ్యాలను అభివృద్ధి చేసుకోవాలనుకుంటున్నారు?",
        "hindi": "आने वाले कुछ वर्षों में आप कौन-सी कौशल विकसित करना चाहते हैं?",
    },
    {
        "id": "question-10",
        "category": "Closing",
        "text": "Is there anything else about your experience you would like to share?",
        "telugu": "మీ అనుభవం గురించి మీరు పంచుకోవాలనుకునే ఇంకేదైనా ఉందా?",
        "hindi": "क्या आप अपने अनुभव के बारे में कुछ और साझा करना चाहेंगे?",
    },
]
ROLE_QUESTIONS = {
    "Software Engineer": [
        "How would you choose a data structure for a feature with frequent lookups and updates?",
        "Describe how you would design an API for a small software product.",
        "How do you test and debug a change before releasing it?",
    ],
    "Frontend Developer": [
        "Explain the difference between useState and useEffect in React.",
        "How would you investigate and optimize a slow React application?",
        "Explain event bubbling in JavaScript and when event delegation is useful.",
    ],
    "Backend Developer": [
        "How would you design a reliable REST API for a service with growing traffic?",
        "How do database indexes help, and what tradeoffs do they introduce?",
        "How would you investigate a slow endpoint and protect it from abuse?",
    ],
    "Full Stack Developer": [
        "How would you design a feature from the browser UI through its API and database?",
        "How do you keep frontend state consistent with backend data?",
        "How would you diagnose a bug that could originate in either the client or server?",
    ],
    "Data Analyst": [
        "How would you use SQL to validate a metric before sharing it with stakeholders?",
        "How do you handle missing values and outliers in a dataset?",
        "How would you explain an unexpected trend and distinguish correlation from causation?",
    ],
    "Data Scientist": [
        "How would you choose an evaluation metric for an imbalanced classification problem?",
        "What steps help prevent data leakage when validating a model?",
        "How would you compare a simple baseline with a more complex model?",
    ],
    "Product Manager": [
        "How would you prioritize two high-impact requests competing for the same team?",
        "How would you define success metrics for a newly launched product feature?",
        "How would you use customer evidence to decide whether to change a roadmap?",
    ],
    "UI/UX Designer": [
        "How would you learn what users need before designing a new workflow?",
        "How do you evaluate whether a prototype solves the usability problem?",
        "How would you balance accessibility, user needs, and business constraints in a design?",
    ],
}

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"], button, input, textarea, select {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    color: #f4f1ff;
    background:
        radial-gradient(ellipse at 12% 0%, rgba(91, 33, 182, .24), transparent 32%),
        radial-gradient(ellipse at 92% 14%, rgba(8, 145, 178, .11), transparent 28%),
        linear-gradient(145deg, #080515 0%, #100923 54%, #090819 100%);
}
[data-testid="stHeader"] { background: rgba(8, 5, 21, .65); }
[data-testid="stToolbar"], [data-testid="stSidebar"], footer { display: none; }
.main .block-container { max-width: 1320px; padding: 1.4rem 2rem 4rem; }
p, label, li, [data-testid="stMarkdownContainer"] { color: #d8d2eb; }
h1, h2, h3, h4 { color: #fcfaff; font-family: 'Manrope', sans-serif; letter-spacing: -.035em; }
h1 { font-size: clamp(2.6rem, 5.3vw, 4.7rem); line-height: 1.06; font-weight: 800; }
h2 { font-weight: 750; }
[data-testid="stCaptionContainer"], .stCaption { color: #9992b5 !important; }
[data-testid="stMetric"] {
    background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.085);
    border-radius: 18px; padding: 16px 18px;
}
[data-testid="stMetricLabel"] { color: #aaa3c1; }
[data-testid="stMetricValue"] { color: #f8f6ff; font-family: 'Manrope', sans-serif; }
[data-testid="stFileUploader"] section, [data-testid="stAudioInput"] {
    background: rgba(255,255,255,.035); border: 1px dashed rgba(167,139,250,.45);
    border-radius: 20px;
}
[data-testid="stFileUploader"] section { padding: 1.6rem; }
[data-testid="stFileUploader"] button, [data-testid="stAudioInput"] button {
    border-radius: 12px;
}
.stButton > button, .stDownloadButton > button {
    border: 1px solid rgba(167,139,250,.35); border-radius: 13px;
    color: #f7f4ff; background: rgba(124,58,237,.16); font-weight: 700;
    min-height: 44px; transition: all .18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: rgba(34,211,238,.65); color: white; background: rgba(124,58,237,.3);
    box-shadow: 0 0 24px rgba(124,58,237,.2); transform: translateY(-1px);
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
    background: linear-gradient(100deg, #6d28d9, #9333ea 60%, #7c3aed);
    border: 1px solid rgba(196,181,253,.5); box-shadow: 0 8px 30px rgba(109,40,217,.24);
}
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
    color: #f8f6ff !important; background: rgba(255,255,255,.045) !important;
    border-color: rgba(255,255,255,.12) !important; border-radius: 12px !important;
}
[data-testid="stExpander"] {
    background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.08);
    border-radius: 16px;
}
[data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg,#7c3aed,#a855f7,#22d3ee); }
[data-testid="stAlert"] { border-radius: 14px; }
.topbar { display:flex; justify-content:space-between; align-items:center; margin:0 0 2rem; }
.brand { display:flex; gap:12px; align-items:center; color:#fff; font:800 1.04rem Manrope,sans-serif; }
.brand-icon {
    width:38px;height:38px;border-radius:13px;display:grid;place-items:center;
    background:linear-gradient(145deg,#8b5cf6,#6d28d9 65%,#22d3ee);
    box-shadow:0 0 26px rgba(139,92,246,.37);font-size:1.1rem;
}
.top-meta { color:#a7a0bc; font-size:.82rem; letter-spacing:.08em; text-transform:uppercase; }
.eyebrow { color:#a78bfa; font-size:.76rem; font-weight:800; letter-spacing:.18em; text-transform:uppercase; }
.hero-copy { color:#aaa4bf; font-size:1.1rem; max-width:560px; line-height:1.8; }
.glass {
    background:linear-gradient(145deg,rgba(30,22,55,.82),rgba(18,15,38,.76));
    border:1px solid rgba(255,255,255,.1); border-radius:24px;
    box-shadow:0 22px 80px rgba(0,0,0,.22), inset 0 1px rgba(255,255,255,.035);
    padding:24px;
}
.glow-card {
    background:radial-gradient(ellipse at 80% 10%,rgba(124,58,237,.28),transparent 42%),
      linear-gradient(145deg,rgba(34,23,65,.95),rgba(14,13,34,.93));
    border:1px solid rgba(167,139,250,.22);border-radius:28px;
    box-shadow:0 0 90px rgba(109,40,217,.16),inset 0 1px rgba(255,255,255,.06);
    padding:30px;
}
.hero-visual {
    min-height:370px; position:relative; overflow:hidden; border-radius:28px;
    background:radial-gradient(circle at 50% 48%,rgba(139,92,246,.24),transparent 38%),
      linear-gradient(145deg,#17102e,#101126 72%,#0c1a2a);
    border:1px solid rgba(167,139,250,.2); padding:24px;
}
.orb {
    position:absolute;width:170px;height:170px;border-radius:50%;left:50%;top:48%;
    transform:translate(-50%,-50%);background:radial-gradient(circle at 35% 30%,#b7a2ff,#7434db 45%,#32146d 76%);
    box-shadow:0 0 75px rgba(139,92,246,.5),inset -20px -20px 45px rgba(10,5,32,.55);
    animation:float 5s ease-in-out infinite;
}
.orbit { position:absolute;left:50%;top:48%;width:270px;height:270px;transform:translate(-50%,-50%) rotate(-24deg);border:1px solid rgba(34,211,238,.24);border-radius:50%; }
.orbit:after { content:'';position:absolute;right:24px;top:45px;width:10px;height:10px;background:#22d3ee;border-radius:50%;box-shadow:0 0 20px #22d3ee; }
.mini-analysis {
    position:absolute;left:23px;bottom:20px;width:70%;padding:17px;
    border:1px solid rgba(255,255,255,.13);border-radius:17px;
    background:rgba(11,8,28,.78);backdrop-filter:blur(14px);
}
.scan-line { height:4px;border-radius:10px;background:linear-gradient(90deg,#8b5cf6,#22d3ee);margin-top:12px; }
.float-chip {
    position:absolute;right:20px;top:24px;padding:10px 13px;border-radius:14px;
    color:#dcd3ff;background:rgba(23,15,47,.85);border:1px solid rgba(167,139,250,.2);
    font-size:.78rem;box-shadow:0 10px 36px rgba(0,0,0,.24);
}
.step-row { display:flex;gap:8px;margin:1.2rem 0 1.6rem; }
.step-node { flex:1;padding:11px 9px;border-radius:13px;text-align:center;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.025);color:#827b9c;font-size:.78rem;font-weight:700; }
.step-node.active { background:rgba(124,58,237,.17);border-color:rgba(167,139,250,.38);color:#e9ddff; }
.step-node.done { color:#9cecf3;border-color:rgba(34,211,238,.2); }
.tag {
    display:inline-block;border:1px solid rgba(167,139,250,.23);border-radius:999px;
    background:rgba(124,58,237,.12);color:#d8c9ff;padding:5px 10px;font-size:.76rem;margin:3px 4px 3px 0;
}
.muted { color:#a7a0bc; }
.divider { height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.12),transparent);margin:23px 0; }
.avatar {
    aspect-ratio:16/10;border-radius:20px;display:grid;place-items:center;position:relative;
    background:radial-gradient(circle at 50% 45%,rgba(139,92,246,.42),transparent 40%),linear-gradient(145deg,#20163e,#0d1125);
    border:1px solid rgba(167,139,250,.22);overflow:hidden;
}
.avatar-face { width:122px;height:145px;border-radius:48% 48% 45% 45%;background:linear-gradient(145deg,#d9cbff,#8a61d6 56%,#482d80);box-shadow:0 0 50px rgba(139,92,246,.42);position:relative; }
.avatar-face:before { content:'';position:absolute;left:25px;top:52px;width:9px;height:5px;border-radius:50%;background:#241642;box-shadow:45px 0 #241642; }
.avatar-face:after { content:'';position:absolute;left:49px;top:78px;width:24px;height:9px;border-bottom:2px solid #482d80;border-radius:50%; }
.wave { display:flex;justify-content:center;align-items:center;gap:4px;height:38px; }
.wave span { width:3px;height:12px;border-radius:4px;background:#a78bfa;animation:wave 1s ease-in-out infinite; }
.wave span:nth-child(2n) { animation-delay:.15s;background:#22d3ee; }
.wave span:nth-child(3n) { animation-delay:.3s; }
@keyframes wave { 0%,100%{height:8px;opacity:.55}50%{height:28px;opacity:1} }
@keyframes float { 0%,100%{transform:translate(-50%,-50%) translateY(0)}50%{transform:translate(-50%,-50%) translateY(-12px)} }
@media(max-width:760px) {
    .main .block-container { padding:1rem 1rem 3rem; }
    .topbar { margin-bottom:1.2rem; }
    .top-meta { display:none; }
    .glass,.glow-card { padding:18px;border-radius:19px; }
    .hero-visual { min-height:320px; }
    .step-row { overflow-x:auto; }
    .step-node { min-width:88px;font-size:.7rem; }
}
</style>
"""


def get_stage_progress(stage_name: str):
    return ["Setup", "Resume Analysis", "AI Interview", "Interview Completed", "Overall Results"]


def check_repeat_question_safe(current_index: int, total_questions: int) -> bool:
    return total_questions > 0 and 0 <= current_index < total_questions


def next_question_after_answer(current_index: int, total_questions: int) -> int:
    return min(max(current_index, 0) + 1, total_questions)


def build_resume_analysis_summary(resume_data, jd_data=None, job_match=None):
    if resume_data is None:
        return {
            "score": 0,
            "strengths": ["Add a resume to begin."],
            "weak_areas": ["No resume yet."],
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": [],
        }
    score = round(getattr(resume_data, "rubric_score", 70.0))
    strengths = list(getattr(resume_data, "strengths", [])[:3]) or [
        "Solid technical base",
        "Project evidence present",
        "Clear learning trajectory",
    ]
    weak_areas = list(getattr(resume_data, "missing_or_unclear", [])[:3]) or list(
        getattr(resume_data, "actionable_improvements", [])[:3]
    ) or ["Add measurable outcomes and role-specific examples"]
    suggestions = [
        "Highlight measurable impact using numbers and business outcomes.",
        "Add one concise example that shows leadership, teamwork, or problem-solving.",
        "Tailor your resume to the target role by emphasizing relevant tools and skills.",
    ]
    match_score = 0
    matched_skills = []
    missing_skills = []
    if job_match is not None:
        match_score = round(getattr(job_match, "match_score", 0.0))
        matched_skills = list(getattr(job_match, "matched_skills", []))
        missing_skills = list(getattr(job_match, "missing_skills", []))
    elif jd_data is not None:
        missing_skills = list(getattr(jd_data, "required_skills", []))
    return {
        "score": score,
        "strengths": strengths,
        "weak_areas": weak_areas,
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
    }


def build_result_cards(summary):
    summary = summary or {}
    overall_score = int(summary.get("overall_score", 0) or 0)
    dimension_scores = summary.get("dimension_scores") or {}
    category_scores = {}
    for name in RESULT_CATEGORY_ORDER:
        if name in dimension_scores:
            category_scores[name] = dimension_scores[name]
        elif name == "Communication":
            category_scores[name] = overall_score
        elif name == "Answer Quality":
            category_scores[name] = max(0, overall_score - 5)
        elif name == "Technical Knowledge":
            category_scores[name] = max(0, overall_score - 10)
        elif name == "Confidence / Presentation":
            category_scores[name] = max(0, overall_score - 12)
        elif name == "Answer Delivery":
            category_scores[name] = max(0, overall_score - 8)
    strengths = summary.get("strengths") or ["Clear communication", "Structured responses"]
    areas = summary.get("areas_to_improve") or ["Answer structure", "Technical depth"]
    return {
        "overall_score": overall_score,
        "category_scores": category_scores,
        "strengths": list(strengths),
        "areas_to_improve": list(areas),
    }


def explain_question_in_language(question_text: str, language: str = "English") -> str:
    normalized = (language or "English").strip().lower()
    base = question_text.strip()
    explanations = {
        "telugu": "ఈ ప్రశ్న మీ అనుభవం లేదా ప్రాజెక్ట్‌ను స్పష్టంగా వివరించమని అడుగుతోంది. నిజమైన ఉదాహరణ, మీ చర్యలు, ఫలితాన్ని చెప్పండి. Consider a difficult project or situation.",
        "hindi": "यह प्रश्न आपके अनुभव या प्रोजेक्ट को स्पष्ट रूप से समझाने के लिए कहता है। वास्तविक उदाहरण, अपने कदम और परिणाम बताइए।",
        "tamil": "இந்தக் கேள்வி உங்கள் அனுபவம் அல்லது திட்டத்தைத் தெளிவாக விளக்கக் கேட்கிறது. உண்மையான எடுத்துக்காட்டு, உங்கள் நடவடிக்கைகள் மற்றும் முடிவைச் சொல்லுங்கள்.",
        "kannada": "ಈ ಪ್ರಶ್ನೆಯು ನಿಮ್ಮ ಅನುಭವ ಅಥವಾ ಯೋಜನೆಯನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ವಿವರಿಸಲು ಕೇಳುತ್ತದೆ. ನಿಜವಾದ ಉದಾಹರಣೆ, ನಿಮ್ಮ ಕ್ರಮಗಳು ಮತ್ತು ಫಲಿತಾಂಶವನ್ನು ತಿಳಿಸಿ.",
        "malayalam": "ഈ ചോദ്യം നിങ്ങളുടെ അനുഭവം അല്ലെങ്കിൽ പ്രോജക്റ്റ് വ്യക്തമായി വിശദീകരിക്കാൻ ആവശ്യപ്പെടുന്നു. യഥാർത്ഥ ഉദാഹരണവും നടപടികളും ഫലവും പറയുക.",
        "marathi": "हा प्रश्न तुमचा अनुभव किंवा प्रकल्प स्पष्टपणे सांगण्यास सांगतो. खरे उदाहरण, तुम्ही केलेल्या कृती आणि परिणाम सांगा.",
        "bengali": "এই প্রশ্নটি আপনার অভিজ্ঞতা বা প্রকল্প স্পষ্টভাবে ব্যাখ্যা করতে বলছে। বাস্তব উদাহরণ, আপনার পদক্ষেপ এবং ফলাফল বলুন।",
    }
    explanation = explanations.get(
        normalized,
        "This question asks you to explain a real example, your approach, and the outcome in a clear, structured way.",
    )
    return f'{explanation} Question: "{base}"'


def _init_state():
    defaults = {
        "stage": "home",
        "resume_data": None,
        "resume_name": "",
        "sample_resume": False,
        "candidate_name": "Candidate",
        "target_role": "Software Engineer",
        "interview_language": "English",
        "interview_questions": [],
        "current_q_index": 0,
        "session_evaluations": [],
        "latest_summary": None,
        "session_started_at": None,
        "interview_paused": False,
        "interview_pause_started": None,
        "interview_paused_seconds": 0,
        "repeat_question_token": 0,
        "recording_command_id": 0,
        "recording_command": "",
        "last_processed_audio_id": None,
        "media_value": {},
        "transcript_error": "",
        "save_history_consent": False,
        "selected_provider": DEFAULT_PROVIDER,
        "custom_api_key": GEMINI_API_KEY,
        "saved_session_id": None,
        "save_history_error": "",
        "confirm_delete_history": False,
        "demo_mode": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _set_stage(stage: str):
    if stage not in STAGES:
        raise ValueError(f"Unknown app stage: {stage}")
    st.session_state.stage = stage
    st.query_params["page"] = stage
    if st.session_state.target_role in ROLE_OPTIONS:
        st.query_params["role"] = st.session_state.target_role


def _route_from_query():
    requested = st.query_params.get("page")
    requested_role = st.query_params.get("role")
    if requested_role in ROLE_OPTIONS:
        st.session_state.target_role = requested_role
    if requested in STAGES:
        st.session_state.stage = requested
    if st.session_state.stage in {"analysis", "interview", "complete", "feedback", "report"} and st.session_state.resume_data is None:
        st.session_state.stage = "home"
    if st.session_state.stage in {"complete", "feedback", "report"} and not st.session_state.session_evaluations:
        st.session_state.stage = "interview"
    st.query_params["page"] = st.session_state.stage
    if st.session_state.target_role in ROLE_OPTIONS:
        st.query_params["role"] = st.session_state.target_role


def _render_header(stage: str):
    st.markdown(
        '<div class="topbar"><div class="brand"><span class="brand-icon">✦</span>'
        '<span>AI Interview Coach</span></div>'
        f'<div class="top-meta">Practice workspace&nbsp;&nbsp; / &nbsp;&nbsp;{html.escape(STAGE_LABELS[stage])}</div></div>',
        unsafe_allow_html=True,
    )
    visible = ["home", "analysis", "interview", "feedback", "report"]
    active = "feedback" if stage == "complete" else stage
    nodes = []
    for item in visible:
        class_name = "active" if item == active else ""
        if STAGES.index(item) < STAGES.index(active):
            class_name = "done"
        nodes.append(f'<div class="step-node {class_name}">{html.escape(STAGE_LABELS[item])}</div>')
    st.markdown(f'<div class="step-row">{"".join(nodes)}</div>', unsafe_allow_html=True)


def _render_hero_visual():
    st.markdown(
        """
        <div class="hero-visual">
          <div class="float-chip">✦ &nbsp; AI practice studio</div>
          <div class="orbit"></div><div class="orb"></div>
          <div class="mini-analysis">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="font-weight:700;color:#f4f1ff">Resume insights</span>
              <span style="color:#22d3ee;font-size:.76rem">READY TO PREVIEW</span>
            </div>
            <div style="color:#a7a0bc;font-size:.8rem;margin-top:9px">Skills · Projects · Practice focus</div>
            <div class="scan-line"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _process_resume_upload(uploaded):
    if uploaded is None or uploaded.name == st.session_state.resume_name:
        return
    if uploaded.name.lower().endswith(".doc"):
        st.error("Legacy .doc files are not supported by the current parser. Save the document as .docx or PDF and upload it again.")
        return
    with st.status("Preparing your resume analysis…", expanded=True) as status:
        st.write("Reading resume file")
        content = extract_text_from_file(uploaded, uploaded.name)
        if not content.strip():
            status.update(label="No readable text found", state="error")
            st.error("This file did not contain extractable text. Try a text-based PDF or DOCX, or use the sample resume.")
            return
        st.write("Analyzing skills, projects, and experience")
        resume_data = parse_resume(content)
        st.session_state.resume_data = resume_data
        st.session_state.resume_name = uploaded.name
        st.session_state.sample_resume = False
        st.session_state.demo_mode = False
        status.update(label="Resume ready", state="complete")


def _load_sample_resume():
    st.session_state.resume_data = parse_resume(SAMPLE_RESUME)
    st.session_state.resume_name = "Sample resume"
    st.session_state.sample_resume = True
    st.session_state.demo_mode = True
    st.session_state.session_evaluations = []
    st.session_state.interview_questions = []
    st.session_state.latest_summary = None
    st.session_state.saved_session_id = None
    _set_stage("analysis")
    st.rerun()


def render_home_page():
    _render_header("home")
    left, right = st.columns([1.08, 0.92], gap="large")
    with left:
        st.markdown('<div class="eyebrow">AI-powered interview preparation</div>', unsafe_allow_html=True)
        st.markdown("# Turn Your Resume Into Interview Confidence.")
        st.markdown(
            '<div class="hero-copy">Upload your resume and practice a personalized AI-powered interview. '
            'Get thoughtful questions and practical feedback grounded in your own experience.</div>',
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(
            '<div style="display:flex;gap:9px;flex-wrap:wrap;margin:12px 0 20px">'
            '<span class="tag">Resume-aware questions</span><span class="tag">Evidence-led coaching</span>'
            '<span class="tag">Private practice</span></div>',
            unsafe_allow_html=True,
        )
        _render_hero_visual()
    with right:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown("### Upload Resume")
        st.session_state.target_role = st.selectbox(
            "Target Role",
            ROLE_OPTIONS,
            index=ROLE_OPTIONS.index(st.session_state.target_role)
            if st.session_state.target_role in ROLE_OPTIONS
            else 0,
            key="target_role_selector",
        )
        st.query_params["role"] = st.session_state.target_role
        st.markdown('<p class="muted">Drop your resume here or browse files. PDF, DOC, DOCX.</p>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Resume file",
            type=["pdf", "doc", "docx"],
            help="PDF and DOCX are parsed locally. Legacy .doc files should be converted to .docx first.",
            label_visibility="collapsed",
            key="resume_upload",
        )
        _process_resume_upload(uploaded)
        if st.session_state.resume_data is not None:
            if st.session_state.sample_resume:
                st.info("Sample data loaded for a demo. It is not your resume.")
            else:
                st.success(f"Resume ready · {st.session_state.resume_name}")
                st.caption(f"{len(st.session_state.resume_data.skills)} skills detected · Parsed on this device")
            if st.button("Review Resume Analysis →", type="primary", use_container_width=True):
                _set_stage("analysis")
                st.rerun()
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("**No resume handy?**")
        if st.button("Explore a sample experience", use_container_width=True):
            _load_sample_resume()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("#### A more useful way to practice")
    feature_cols = st.columns(4)
    features = [
        ("01", "Grounded in you", "Questions start from skills and projects in your resume."),
        ("02", "Clear feedback", "See answer evidence, strengths, and a practical next step."),
        ("03", "Your language", "Practice questions in English, Telugu, Hindi, and more."),
        ("04", "Progress that matters", "Review your rubric and build a focused practice plan."),
    ]
    for col, (number, title, body) in zip(feature_cols, features):
        with col:
            st.markdown(
                f'<div class="glass" style="min-height:158px"><div class="eyebrow">{number}</div>'
                f'<h4 style="margin:12px 0 6px">{title}</h4><span class="muted">{body}</span></div>',
                unsafe_allow_html=True,
            )


def _render_analysis_page():
    _render_header("analysis")
    resume = st.session_state.resume_data
    if resume is None:
        st.warning("Upload a resume or choose the sample experience to continue.")
        if st.button("Back to upload"):
            _set_stage("home")
            st.rerun()
        return

    st.markdown('<div class="eyebrow">Your profile, understood</div>', unsafe_allow_html=True)
    st.title("Your Resume Is Ready")
    if st.session_state.sample_resume:
        st.info("Demo preview · The resume and any generated feedback in this session use sample data.")
    st.markdown(
        "Review the profile summary below. Your practice feedback is guidance from the built-in rubric—not a hiring prediction."
    )
    summary = build_resume_analysis_summary(resume)
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">AI interview readiness</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font:800 3.6rem Manrope,sans-serif;color:#fff;margin:8px 0">{summary["score"]}'
            '<span style="font-size:1.25rem;color:#a7a0bc"> / 100</span></div>',
            unsafe_allow_html=True,
        )
        st.caption("Resume rubric estimate · based on parsed resume content")
        st.markdown(f'**Target role**<br><span class="muted">{html.escape(st.session_state.target_role)}</span>', unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("**Skills detected**")
        skills = resume.skills[:12]
        st.markdown(
            " ".join(f'<span class="tag">{html.escape(skill)}</span>' for skill in skills)
            if skills else '<span class="muted">No skills detected yet.</span>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("#### Strengths")
        for strength in summary["strengths"][:4]:
            st.markdown(f"- ✦ {strength}")
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("#### Improvement areas")
        for area in summary["weak_areas"][:4]:
            st.markdown(f"- ↗ {area}")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("")
    st.markdown("#### Set up your practice")
    role_col, name_col = st.columns(2)
    with role_col:
        st.session_state.target_role = st.selectbox(
            "Target role",
            ROLE_OPTIONS,
            index=ROLE_OPTIONS.index(st.session_state.target_role)
            if st.session_state.target_role in ROLE_OPTIONS
            else 0,
            key="target_role_selector",
        )
        st.query_params["role"] = st.session_state.target_role
    with name_col:
        st.session_state.candidate_name = st.text_input("Name for this session", value=st.session_state.candidate_name, key="candidate_name_input")
    st.session_state.save_history_consent = st.checkbox(
        "Save my answer transcripts and results to local interview history on this device.",
        value=st.session_state.save_history_consent,
        help="Leave unchecked to keep this session's results in memory only. You can still download the report.",
    )
    if st.button("Continue to Interview →", type="primary", use_container_width=True):
        st.session_state.interview_questions = _create_questions(resume, st.session_state.target_role)
        st.session_state.current_q_index = 0
        st.session_state.session_evaluations = []
        st.session_state.latest_summary = None
        st.session_state.saved_session_id = None
        st.session_state.save_history_error = ""
        st.session_state.session_started_at = time.time()
        st.session_state.interview_paused = False
        _set_stage("interview")
        st.rerun()


def _create_questions(resume, target_role: str):
    project = resume.projects[0].get("title", "a technical project") if resume.projects else "a technical project"
    role_questions = ROLE_QUESTIONS.get(target_role, ROLE_QUESTIONS["Software Engineer"])
    questions = []
    for idx, item in enumerate(QUESTION_BANK):
        text = item["text"]
        if idx == 1:
            text = f"Walk me through your project '{project}' and the part you contributed."
        elif idx == 3:
            text = f"Why are you interested in the {target_role} role and this kind of work?"
        elif idx in (2, 5, 6):
            text = role_questions[(2, 5, 6).index(idx)]
        questions.append(
            Question(
                id=item["id"],
                text=text,
                mode=item["category"],
                difficulty="Medium",
                provenance=f"Personalized for the selected {target_role} role and interview flow.",
                target_dimension=(
                    "Structure"
                    if item["category"] in {"Behavioral", "Introduction"}
                    else "Relevance"
                    if target_role == "Product Manager"
                    else "Technical Depth"
                ),
            )
        )
    return questions


def _question_text(index: int, language: str, question: Question):
    translation_key = language.lower()
    if index in (2, 5, 6):
        return question.text
    if translation_key in {"telugu", "hindi"} and index < len(QUESTION_BANK):
        return QUESTION_BANK[index][translation_key]
    return question.text


def _decode_recording_to_wav(audio_data: str) -> bytes:
    """Decode the browser's MediaRecorder container into mono 16 kHz WAV."""
    encoded_audio = base64.b64decode(audio_data, validate=True)
    resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)
    pcm_chunks = []
    with av.open(io.BytesIO(encoded_audio)) as container:
        audio_stream = next((stream for stream in container.streams if stream.type == "audio"), None)
        if audio_stream is None:
            raise ValueError("The recording does not contain an audio track.")
        for frame in container.decode(audio_stream):
            resampled = resampler.resample(frame)
            if not isinstance(resampled, list):
                resampled = [resampled] if resampled is not None else []
            pcm_chunks.extend(chunk.to_ndarray().tobytes() for chunk in resampled)
    if not pcm_chunks:
        raise ValueError("No audio samples were found in the recording.")
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b"".join(pcm_chunks))
    return output.getvalue()


def _render_candidate_video(question_text: str, index: int):
    st.markdown("#### YOU")
    st.caption("Camera video is not analyzed or saved. Microphone audio is recorded only when you start an answer.")
    st.caption("Allow access in your browser when the permission prompt appears. Use localhost or HTTPS.")
    value = interview_media(
        question=question_text,
        questionIndex=index,
        language=st.session_state.interview_language,
        paused=st.session_state.interview_paused,
        repeatToken=st.session_state.repeat_question_token,
        languageTag=LANGUAGE_TAGS.get(st.session_state.interview_language, "en-IN"),
        recordingCommand=st.session_state.recording_command,
        recordingCommandId=st.session_state.recording_command_id,
        default={"mediaState": "requesting", "recordingState": "ready", "speechState": "speaking"},
        key="interview_media",
    )
    if value:
        last_audio_id = st.session_state.last_processed_audio_id
        if value.get("audioId") == last_audio_id:
            value = {key: item for key, item in value.items() if key != "audioData"}
        st.session_state.media_value = value
    return st.session_state.media_value


@st.fragment(run_every=1)
def _render_timer():
    started = st.session_state.session_started_at or time.time()
    now = time.time()
    paused_seconds = st.session_state.interview_paused_seconds
    if st.session_state.interview_paused and st.session_state.interview_pause_started:
        paused_seconds += now - st.session_state.interview_pause_started
    elapsed = max(0, int(now - started - paused_seconds))
    minutes, seconds = divmod(elapsed, 60)
    st.markdown(
        f'<div style="text-align:right;color:#a7a0bc;padding-top:14px">◷ &nbsp; {minutes:02d}:{seconds:02d}'
        f' &nbsp; · &nbsp; {html.escape(st.session_state.target_role)}</div>',
        unsafe_allow_html=True,
    )


def _toggle_interview_pause():
    if st.session_state.interview_paused:
        paused_at = st.session_state.interview_pause_started
        if paused_at:
            st.session_state.interview_paused_seconds += time.time() - paused_at
        st.session_state.interview_pause_started = None
        st.session_state.interview_paused = False
        st.session_state.interview_pause_started = None
        st.session_state.interview_paused_seconds = 0
        st.session_state.repeat_question_token = 0
        st.session_state.recording_command_id = 0
        st.session_state.recording_command = ""
        st.session_state.last_processed_audio_id = None
        st.session_state.media_value = {}
        st.session_state.transcript_error = ""
    else:
        st.session_state.interview_pause_started = time.time()
        st.session_state.interview_paused = True


def _process_recorded_audio(value, index: int):
    audio_data = value.get("audioData") if isinstance(value, dict) else None
    audio_id = value.get("audioId") if isinstance(value, dict) else None
    if not audio_data or audio_id == st.session_state.last_processed_audio_id:
        return
    st.session_state.last_processed_audio_id = audio_id
    st.session_state.media_value = {
        key: item for key, item in value.items() if key != "audioData"
    }
    answer_key = f"answer_text_{index}"
    if st.session_state.get(answer_key, "").strip():
        st.session_state.transcript_error = "Typed answer kept; the recording was not sent for transcription."
        return
    try:
        with st.spinner("Processing your recording and preparing a transcript…"):
            wav_audio = _decode_recording_to_wav(audio_data)
            transcript = transcribe_audio_bytes(wav_audio)
    except (ValueError, OSError, EOFError, binascii.Error, av.error.FFmpegError) as error:
        st.session_state.transcript_error = f"Recording could not be processed: {error}. You can type your answer instead."
        return
    if transcript:
        st.session_state[answer_key] = transcript
        st.session_state.transcript_error = "Transcript ready. Review or edit it before submitting your answer."
    else:
        st.session_state.transcript_error = "No transcript was detected. You can type your answer instead."


def _render_interview_page():
    questions = st.session_state.interview_questions
    if not questions:
        st.warning("Start from resume analysis to prepare your interview.")
        if st.button("Return to resume analysis"):
            _set_stage("analysis")
            st.rerun()
        return
    index = st.session_state.current_q_index
    if index >= len(questions):
        _set_stage("complete")
        st.rerun()
        return
    question = questions[index]
    total = len(questions)
    _render_header("interview")
    top_left, top_right = st.columns([2, 1])
    with top_left:
        st.markdown('<div class="eyebrow">Live practice session</div>', unsafe_allow_html=True)
        st.markdown(f"**Interview Role** · {st.session_state.target_role}")
    with top_right:
        _render_timer()
    q_col, lang_col = st.columns([2, 1])
    with q_col:
        st.subheader(f"Question {index + 1} / {total}")
    language_names = [label for label, _ in LANGUAGES]
    language_values = [value for _, value in LANGUAGES]
    current_language_index = language_values.index(st.session_state.interview_language)
    with lang_col:
        selected_label = st.selectbox(
            "Language",
            language_names,
            index=current_language_index,
            key="language_select",
        )
        st.session_state.interview_language = language_values[language_names.index(selected_label)]
    st.progress((index + 1) / total)
    shown_question = _question_text(index, st.session_state.interview_language, question)
    video_left, video_right = st.columns(2, gap="large")
    with video_left:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        media_value = _render_candidate_video(shown_question, index)
        st.markdown("</div>", unsafe_allow_html=True)
    with video_right:
        st.markdown('<div class="glass"><h4 style="margin-top:0">AI INTERVIEWER</h4>', unsafe_allow_html=True)
        st.markdown(
            '<div class="avatar"><div class="avatar-face"></div><div style="position:absolute;bottom:10px;'
            'left:0;right:0;text-align:center;color:#ddd3ff;font-size:.82rem;font-weight:700">AI Interviewer</div></div>',
            unsafe_allow_html=True,
        )
        speech_state = media_value.get("speechState", "speaking") if isinstance(media_value, dict) else "speaking"
        if speech_state == "speaking":
            st.markdown('<div class="wave" aria-label="AI interviewer audio waveform">' + "".join("<span></span>" for _ in range(15)) + "</div>", unsafe_allow_html=True)
            st.caption("🔊 AI is speaking…")
        elif speech_state == "unsupported":
            st.warning(media_value.get("speechError", "Spoken questions are not supported by this browser."))
        elif speech_state == "speech-error":
            st.warning(media_value.get("speechError", "Question audio could not be played. Use Repeat Question or check browser audio settings."))
        elif st.session_state.interview_paused:
            st.caption("Interview Paused")
        else:
            st.caption("🎤 Your turn")
        st.markdown("</div>", unsafe_allow_html=True)
    media_state = media_value.get("mediaState", "requesting") if isinstance(media_value, dict) else "requesting"
    if media_state in {"camera-denied", "permission-denied"}:
        st.error(media_value.get("error", "Camera access is required for video interviews."))
    elif media_state == "microphone-denied":
        st.warning("Microphone unavailable. You can still use the text-answer fallback.")
    elif media_state in {"insecure-context", "unavailable"}:
        st.error(media_value.get("error", "Camera and microphone require localhost or a secure HTTPS connection."))
    elif media_state == "device-ended":
        st.warning(media_value.get("error", "Camera or microphone access ended."))
    if media_value.get("speechError"):
        st.warning(media_value["speechError"])
    if st.session_state.interview_language != "English":
        st.info("Translated prompts are demos. Speech recognition currently transcribes English responses.")
    st.markdown(
        f'<div class="glow-card" style="margin-top:1rem"><div class="eyebrow">{html.escape(question.mode)}</div>'
        f'<div style="font:700 clamp(1.35rem,2.5vw,2rem) Manrope,sans-serif;line-height:1.45;color:#fff;margin-top:12px">'
        f'{html.escape(shown_question)}</div></div>',
        unsafe_allow_html=True,
    )
    _process_recorded_audio(media_value, index)
    qcol1, qcol2, qcol3 = st.columns(3)
    with qcol1:
        if st.button("🔊 Repeat Question", use_container_width=True, disabled=st.session_state.interview_paused):
            st.session_state.repeat_question_token += 1
            st.rerun()
    with qcol2:
        if st.button("💡 Explain", use_container_width=True):
            st.info(explain_question_in_language(shown_question, st.session_state.interview_language))
    with qcol3:
        pause_label = "▶ Resume Interview" if st.session_state.interview_paused else "⏸ Pause Interview"
        if st.button(pause_label, use_container_width=True):
            _toggle_interview_pause()
            st.rerun()
    if st.session_state.interview_paused:
        st.warning("Interview Paused")
        if st.button("End Interview"):
            _set_stage("complete")
            st.rerun()
    st.markdown("")
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("#### YOUR ANSWER")
    st.caption("Recording is sent to the app for this session only. Typed answers remain a fallback. Video is never used for scoring.")
    answer_key = f"answer_text_{index}"
    if st.session_state.transcript_error:
        if "Transcript ready" in st.session_state.transcript_error:
            st.success(st.session_state.transcript_error)
        else:
            st.info(st.session_state.transcript_error)
    answer_text = st.text_area(
        "Answer by typing or correct your transcript",
        key=answer_key,
        height=150,
        placeholder="Start with a direct response, then share a specific example and what you learned…",
        disabled=st.session_state.interview_paused,
    )
    recording_state = media_value.get("recordingState", "ready") if isinstance(media_value, dict) else "ready"
    microphone_available = bool(media_value.get("microphoneAvailable")) if isinstance(media_value, dict) else False
    if recording_state == "recording":
        st.info("Recording…")
    elif recording_state == "paused":
        st.warning("Recording paused")
    elif recording_state == "processing":
        st.info("Processing…")
    record_start, record_pause, record_finish = st.columns(3)
    with record_start:
        if st.button(
            "Start Answer",
            use_container_width=True,
            disabled=(
                st.session_state.interview_paused
                or not microphone_available
                or recording_state in {"recording", "paused", "processing"}
            ),
        ):
            st.session_state.recording_command_id += 1
            st.session_state.recording_command = "start"
            st.rerun()
    with record_pause:
        if st.button(
            "Pause Recording",
            use_container_width=True,
            disabled=st.session_state.interview_paused or recording_state not in {"recording", "paused"},
        ):
            st.session_state.recording_command_id += 1
            st.session_state.recording_command = "pause"
            st.rerun()
    with record_finish:
        if st.button(
            "Finish Recording",
            use_container_width=True,
            disabled=recording_state not in {"recording", "paused"},
        ):
            st.session_state.recording_command_id += 1
            st.session_state.recording_command = "finish"
            st.rerun()
    if st.button(
        "Finish Answer →" if index < total - 1 else "Finish Interview →",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.interview_paused,
    ):
        final_answer = (answer_text or "").strip()
        if not final_answer:
            st.error("No answer is ready yet. Record and finish an answer, or type your answer above.")
        else:
            provider = get_ai_provider(st.session_state.selected_provider, st.session_state.custom_api_key)
            evaluation = provider.evaluate_answer(
                question=question,
                answer_text=final_answer,
                raw_transcript=final_answer,
                resume=st.session_state.resume_data,
            )
            st.session_state.session_evaluations.append(evaluation)
            st.session_state.transcript_error = ""
            st.session_state.current_q_index += 1
            st.session_state.last_processed_audio_id = None
            if st.session_state.current_q_index >= total:
                _set_stage("complete")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Your answers are evaluated using the practice rubric. No hiring decisions or personality judgments are made.")


def _ensure_summary():
    if st.session_state.latest_summary is None and st.session_state.session_evaluations:
        summary = summarize_session(
            candidate_name=st.session_state.candidate_name,
            target_role=st.session_state.target_role,
            interview_mode="Personalized mock interview",
            difficulty="Medium",
            evaluations=st.session_state.session_evaluations,
        )
        st.session_state.latest_summary = summary
    summary = st.session_state.latest_summary
    if summary is not None and st.session_state.save_history_consent and st.session_state.saved_session_id != summary.session_id:
        if not save_session(summary):
            st.session_state.save_history_error = "Results could not be saved to local history. Your report remains available in this session."
        st.session_state.saved_session_id = summary.session_id
    if st.session_state.save_history_error:
        st.warning(st.session_state.save_history_error)
    return summary


def _render_complete_page():
    summary = _ensure_summary()
    _render_header("complete")
    st.markdown('<div class="eyebrow">Session complete</div>', unsafe_allow_html=True)
    st.title("Interview Complete")
    st.markdown("### Analyzing your performance…")
    st.markdown(
        '<div class="glass"><div class="wave">' + "".join("<span></span>" for _ in range(21)) +
        '</div><p style="text-align:center;color:#c8c0da">Reviewing your answers against the transparent practice rubric</p></div>',
        unsafe_allow_html=True,
    )
    if summary is None:
        st.error("There are no completed answers to analyze. Return to the interview and answer at least one question.")
        if st.button("Return to Interview"):
            _set_stage("interview")
            st.rerun()
        return
    st.metric("Practice score", f"{summary.overall_score} / 100")
    st.caption(f"{len(st.session_state.session_evaluations)} of 10 answers evaluated. This is practice guidance, not a hiring prediction.")
    if st.button("View Feedback →", type="primary", use_container_width=True):
        _set_stage("feedback")
        st.rerun()


def _communication_score(scores):
    values = [scores[key] for key in ("Clarity", "Relevance", "Conciseness") if key in scores]
    return round(sum(values) / len(values)) if values else None


def _render_feedback_page():
    summary = _ensure_summary()
    _render_header("feedback")
    if summary is None:
        st.info("Complete an interview answer to see your feedback.")
        if st.button("Go to interview"):
            _set_stage("interview")
            st.rerun()
        return
    st.markdown('<div class="eyebrow">Your practice debrief</div>', unsafe_allow_html=True)
    st.title("Your Interview Performance")
    st.markdown("Your rubric scores are based on the answers you submitted. They are for practice and improvement—not hiring decisions.")
    st.markdown('<div class="glow-card">', unsafe_allow_html=True)
    score_col, note_col = st.columns([1, 2])
    with score_col:
        st.markdown('<div class="eyebrow">Overall practice score</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font:800 4rem Manrope;color:#fff">{summary.overall_score}<span style="font-size:1.2rem;color:#a7a0bc"> / 100</span></div>', unsafe_allow_html=True)
        st.caption(summary.readiness_explanation)
    with note_col:
        st.markdown("#### Your rubric snapshot")
        scores = summary.dimension_scores
        clarity = _communication_score(scores)
        metrics = [
            ("Clarity", scores.get("Clarity")),
            ("Communication", clarity),
            ("Technical knowledge", scores.get("Technical Depth")),
            ("Answer quality", scores.get("Structure")),
        ]
        columns = st.columns(4)
        for col, (label, score) in zip(columns, metrics):
            with col:
                st.metric(label, f"{score:.0f}" if score is not None else "—")
    st.markdown("</div>", unsafe_allow_html=True)
    strengths = [evaluation.key_strength.split(" — ")[-1] for evaluation in st.session_state.session_evaluations[:3]]
    improvements = [
        evaluation.dimensions[
            min(evaluation.dimensions, key=lambda name: evaluation.dimensions[name].score)
        ].actionable_improvement
        for evaluation in st.session_state.session_evaluations[:3]
    ]
    good_col, improve_col = st.columns(2, gap="large")
    with good_col:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("#### WHAT YOU DID WELL")
        for item in strengths or ["Complete another answer to uncover a strength."]:
            st.markdown(f"- ✦ {item}")
        st.markdown("</div>", unsafe_allow_html=True)
    with improve_col:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("#### AREAS TO IMPROVE")
        for item in improvements or ["Complete another answer to identify a practice focus."]:
            st.markdown(f"- ↗ {item}")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("")
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("#### AI RECOMMENDATIONS")
    for action in summary.top_3_actions:
        st.markdown(f"- {action}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("### Question-by-question feedback")
    for index, evaluation in enumerate(st.session_state.session_evaluations, start=1):
        with st.expander(f"Question {index} · {evaluation.overall_score:.0f} / 100 · {evaluation.question_text}"):
            st.markdown("**Your answer**")
            st.write(evaluation.edited_transcript)
            st.markdown(f"**Strength:** {evaluation.key_strength}")
            st.markdown(f"**Improvement:** {evaluation.priority_weakness}")
            st.markdown("**Evidence**")
            for dimension in evaluation.dimensions.values():
                if dimension.evidence_quotes:
                    st.caption(f'{dimension.dimension}: “{dimension.evidence_quotes[0]}”')
    action_left, action_right = st.columns(2)
    with action_left:
        if st.button("Practice Again", use_container_width=True):
            _reset_for_new_interview()
            _set_stage("home")
            st.rerun()
    with action_right:
        if st.button("View Overall Report →", type="primary", use_container_width=True):
            _set_stage("report")
            st.rerun()


def _report_dimension_scores(summary):
    scores = summary.dimension_scores
    communication = _communication_score(scores)
    return [
        ("Technical Knowledge", scores.get("Technical Depth")),
        ("Communication", communication),
        ("Clarity / delivery", scores.get("Clarity")),
        ("Problem Solving", scores.get("Specificity")),
        ("Behavioral structure", scores.get("Structure")),
    ]


def _render_report_page():
    summary = _ensure_summary()
    _render_header("report")
    if summary is None:
        st.info("Your report will appear after you complete an interview answer.")
        if st.button("Go to interview"):
            _set_stage("interview")
            st.rerun()
        return
    st.markdown('<div class="eyebrow">A practical snapshot of your progress</div>', unsafe_allow_html=True)
    st.title("Your Interview Report")
    st.markdown("A complete overview of your practice session and where to focus next.")
    left, right = st.columns([1, 1.25], gap="large")
    with left:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">INTERVIEW READINESS · PRACTICE INDICATOR</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font:800 4.2rem Manrope;color:#fff;margin:14px 0">{summary.readiness_score:.0f}<span style="font-size:1.3rem;color:#a7a0bc"> / 100</span></div>', unsafe_allow_html=True)
        st.markdown(f'**{html.escape(summary.readiness_band)}**')
        st.caption("Rubric-based practice indicator. Not a prediction of hiring or employment decisions.")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("#### Performance breakdown")
        for label, score in _report_dimension_scores(summary):
            if score is None:
                continue
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;margin:13px 0 6px">'
                f'<span>{html.escape(label)}</span><strong>{score:.0f}</strong></div>'
                f'<div style="height:7px;background:rgba(255,255,255,.08);border-radius:9px">'
                f'<div style="height:7px;width:{max(0, min(100, score)):.0f}%;background:linear-gradient(90deg,#7c3aed,#22d3ee);border-radius:9px"></div></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    strengths_col, improvements_col = st.columns(2, gap="large")
    with strengths_col:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("#### Strengths")
        for item in summary.strongest_answers:
            st.markdown(f"- ✦ {item}")
        st.markdown("</div>", unsafe_allow_html=True)
    with improvements_col:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("#### Improvement areas")
        for item in summary.priority_weaknesses:
            st.markdown(f"- ↗ {item}")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("### Your 7-day practice plan")
    if summary.practice_roadmap:
        for day in summary.practice_roadmap:
            with st.expander(f'{day["day"]} · {day["topic"]}'):
                st.write(day["activity"])
                st.caption(f'Target: {day["target_metric"]}')
    else:
        st.info("Complete more answers to generate a personalized practice plan.")
    report_md = generate_markdown_report(
        summary=summary,
        resume=st.session_state.resume_data,
    )
    start_col, download_col = st.columns(2)
    with start_col:
        if st.button("Start Another Interview", type="primary", use_container_width=True):
            _reset_for_new_interview()
            _set_stage("home")
            st.rerun()
    with download_col:
        st.download_button(
            "Download Report",
            data=report_md,
            file_name="ai_interview_coach_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with st.expander("Privacy controls"):
        st.caption("Saved interview history is stored in the local SQLite database. Deletion removes all saved sessions on this device.")
        if st.button("Delete all saved interview history", key="delete_history"):
            st.session_state.confirm_delete_history = True
        if st.session_state.confirm_delete_history:
            st.warning("This permanently deletes all saved interview sessions on this device.")
            delete_col, cancel_col = st.columns(2)
            with delete_col:
                if st.button("Confirm deletion", key="confirm_delete_history_button"):
                    if delete_all_history():
                        st.session_state.confirm_delete_history = False
                        st.success("Saved interview history has been deleted.")
                    else:
                        st.error("Interview history could not be deleted.")
            with cancel_col:
                if st.button("Cancel deletion", key="cancel_delete_history_button"):
                    st.session_state.confirm_delete_history = False


def _reset_for_new_interview():
    st.session_state.interview_questions = []
    st.session_state.current_q_index = 0
    st.session_state.session_evaluations = []
    st.session_state.latest_summary = None
    st.session_state.session_started_at = None
    st.session_state.saved_session_id = None
    st.session_state.save_history_error = ""
    st.session_state.interview_paused = False
    st.session_state.interview_pause_started = None
    st.session_state.interview_paused_seconds = 0
    st.session_state.recording_command_id = 0
    st.session_state.recording_command = ""
    st.session_state.last_processed_audio_id = None
    st.session_state.media_value = {}
    st.session_state.transcript_error = ""
    st.session_state["target_role_selector"] = st.session_state.target_role


def run_app():
    st.set_page_config(
        page_title="AI Interview Coach",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    _init_state()
    _route_from_query()
    stage = st.session_state.stage
    if stage == "home":
        render_home_page()
    elif stage == "analysis":
        _render_analysis_page()
    elif stage == "interview":
        _render_interview_page()
    elif stage == "complete":
        _render_complete_page()
    elif stage == "feedback":
        _render_feedback_page()
    else:
        _render_report_page()
