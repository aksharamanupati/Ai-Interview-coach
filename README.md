# 🎓 AI Interview Coach

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![Architecture](https://img.shields.io/badge/Architecture-Modular%20Dual--Engine-green.svg)](https://github.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent, adaptive AI-powered interview preparation and coaching platform built specifically for college students, freshers, and campus placement candidates.

> **Core USP:**  
> *"An AI Interview Coach that learns from every interview and automatically adapts the next interview based on the candidate's weaknesses."*

---

## 🚀 Key Highlights & PRD Compliance

1. **Evidence-Based Coaching Over Simple Scoring:** Every score includes verbatim quotes from the candidate's transcript, transparent rationale, and an actionable fix.
2. **Resume & Job Description Gap Analysis:** Real PDF, DOCX, and TXT resume parsing with skills extraction, education audit, and a JD vs Resume Coverage Matrix with verification questions.
3. **Pluggable Dual-Engine Architecture:**
   - **Offline Engine:** High-accuracy deterministic NLP and linguistic rubric scorer (100% offline, zero API keys required).
   - **Gemini Engine:** Optional Google Generative AI (`gemini-2.5-flash`) integration with graceful automatic fallback.
4. **Adaptive Follow-Up Engine:** Automatically triggers clarifying probes when answers are vague, incomplete, or introduce unverified technical claims.
5. **Speech & Camera Practice with Ethical Guardrails:**
   - Voice input via speech-to-text with full text-fallback.
   - Text-to-speech audio question reading.
   - **Mandatory Transcript Correction:** Candidates can review and edit transcribed text before evaluation to eliminate speech recognition errors.
   - Optional camera practice focusing solely on objective presentation pacing (WPM, pauses, framing). **Appearance, beauty, skin color, gender, and accent are strictly excluded from evaluation.**
6. **"Improve My Answer" Engine:** Restructures weak answers into the professional STAR framework while preserving the candidate's actual experience (never fabricating facts or unearned achievements).
7. **Next Interview Engine (USP):** Automatically identifies the candidate's lowest-scoring dimensions from prior sessions and configures the next interview to target those deficits.
8. **Multi-Session Progress Tracking & Comparison:** Measures performance trajectories across Session 1 vs Session 2 to verify measurable skill development.
9. **Personalized 7-Day Practice Roadmap & Audit Report Export:** Generates day-by-day practice plans and downloadable Markdown audit reports.

---

## 🏛️ Project Structure

```text
ai-interview-coach/
│
├── app.py                      # Interactive Streamlit application
├── config.py                   # Central configurations, rubric bands, paths, secrets
├── requirements.txt            # Project dependencies
├── test_suite.py               # Comprehensive automated test suite (11 unit/integration tests)
├── PRD.md                      # Canonical Product Requirements Document
├── MASTER_PROMPT.md            # Master prompt and engineering contract
├── README.md                   # System documentation
│
├── core/                       # Data schemas and models
│   ├── __init__.py
│   └── models.py               # ResumeData, JobDescriptionData, Question, AnswerEvaluation, etc.
│
├── parsers/                    # Multi-format document parsers & gap analysis
│   ├── __init__.py
│   ├── resume_parser.py        # PDF/DOCX/TXT parser and rubric auditor
│   ├── jd_parser.py            # Job description parser
│   └── gap_analyzer.py         # JD vs Resume Coverage Matrix
│
├── ai_providers/               # Dual inference provider layer
│   ├── __init__.py             # Factory loader
│   ├── base.py                 # Abstract Base Class
│   ├── offline_provider.py     # Deterministic NLP & linguistic rubric scorer
│   └── gemini_provider.py      # Google Gemini LLM provider with offline fallback
│
├── interview/                  # Interview orchestration & adaptation
│   ├── __init__.py
│   ├── question_engine.py      # Role-grounded question generator with provenance
│   ├── followup_engine.py      # Adaptive follow-up generator
│   └── next_interview_engine.py # Weakness remediation & Session N vs N+1 comparator
│
├── evaluation/                 # Scoring, readiness, and roadmap
│   ├── __init__.py
│   ├── readiness_calculator.py # Non-predictive practice readiness indicator
│   ├── roadmap_generator.py    # 7-day personalized practice roadmap
│   └── rubric_scorer.py        # 6-dimension session aggregator
│
├── audio/                      # Speech-to-text and Text-to-speech
│   ├── __init__.py
│   └── speech_handler.py       # STT and gTTS audio synthesis
│
├── camera/                     # Optional presentation analysis
│   ├── __init__.py
│   └── presentation_tracker.py # Speaking pace (WPM) and ethical guardrails
│
├── storage/                    # Multi-session SQLite persistence
│   ├── __init__.py
│   └── session_db.py           # Session database and privacy deletion
│
└── ui/                         # UI utilities & exporters
    ├── __init__.py
    └── report_exporter.py      # Markdown & printable report generator
```

---

## 🏃 How to Run the Project

### 1. Run the Streamlit Application
```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Interview practice flow

The Streamlit app provides a guided flow: resume upload → resume analysis → ten-question interview → answer feedback → downloadable report. Navigation is reflected in the `?page=` URL parameter. Use **Explore a sample experience** to preview the flow without uploading a resume; sample data is labelled as demo data.

The interview requests camera and microphone access when the interview opens. A browser component displays the real camera stream, speaks questions using the browser's Web Speech API, and records answer audio with MediaRecorder. The live camera stream is not analyzed or saved. Recordings are sent to Google's speech-recognition service only after you finish recording and only when you have not entered a typed answer; typed answers remain available if permissions are denied. Browser speech voice availability varies; the closest installed voice is selected. The selected role is stored in the interview URL and used to generate role-specific questions. Telugu and Hindi demo question translations are available; question scoring and speech transcription currently support English responses. Saved transcript history is optional and requires separate consent, and the report page includes a delete-history control.

Resume parsing supports text-based PDF and DOCX files. Legacy binary DOC files must be converted to PDF or DOCX before upload. Camera and microphone access require a secure browser context (localhost or HTTPS).

### 2. Run the Automated Test Suite
```powershell
python -m unittest test_suite.py
```

---

## 🛡️ Safety, Fairness & Transparency Guarantees
- **No Hiring Predictions:** All scores are transparently labeled as practice guidance.
- **No Sensitive Trait Scoring:** Physical appearance, race, gender, accent, or attractiveness are never evaluated.
- **Transcript Correction Supported:** Candidates can correct any mis-transcribed speech before evaluation.
- **Fact Preservation:** Answer rewrites never invent fake achievements or employment claims.
- **Zero Key Leakage:** Sensitive keys are masked in UI and logs.
- **Data Privacy:** Users can delete all saved session data at any time via the sidebar button.
