# AI Interview Coach — Product Requirements Document (PRD)

## 1. Product Overview
**Product Name:** AI Interview Coach  
**Product Type:** AI-powered interview preparation and coaching platform  
**Primary Users:** College students, freshers, campus-placement candidates, and early-career job seekers

### Product Vision
Help candidates improve interview performance through personalized practice, evidence-based feedback, targeted coaching, and measurable progress across sessions.

### Core Value Proposition
An AI interview coach that uses the candidate's resume, target role, optional job description, and prior practice history to create relevant interviews and turn weaknesses into focused practice.

### Product Principles
- Coaching over simple scoring.
- Evidence over unsupported judgments.
- Candidate experience over unnecessary complexity.
- Practice guidance, not hiring prediction.
- Privacy and consent by default.
- Every automated score must be explainable and revisable when the underlying transcript is corrected.

## 2. Problem Statement
Candidates often practice with generic questions and receive feedback that is too vague to act on. They need a system that can:
- Practice questions relevant to their background and target role.
- Identify specific weaknesses in answers.
- Explain why an answer was weak or strong.
- Provide a better answer structure without inventing experience.
- Recommend what to practice next.
- Show meaningful improvement across sessions.

## 3. Goals and Non-Goals

### Goals
1. Analyze a candidate's resume.
2. Analyze an optional job description.
3. Identify role-relevant skills and evidence from the resume.
4. Generate personalized interview questions.
5. Conduct realistic voice-based mock interviews.
6. Support optional camera-based practice.
7. Ask adaptive follow-up questions.
8. Analyze answers using defined rubrics.
9. Provide evidence-backed feedback and actionable coaching.
10. Generate improved answer structures that preserve the candidate's real experience.
11. Track weaknesses and improvement over multiple sessions.
12. Generate a practice plan and session report.

### Non-Goals
- Predicting whether a candidate will be hired.
- Making employment decisions for recruiters.
- Inferring or scoring protected/sensitive personal attributes.
- Diagnosing personality, mental health, or character.
- Replacing professional recruiters or human interviewers.
- Treating camera signals as reliable evidence of honesty, competence, confidence, or personality.

## 4. Target User Journey
Registration → Consent & Profile → Resume Upload → Resume Analysis → Optional JD Upload → Resume/JD Gap Analysis → Interview Setup → Personalized Interview → Answer Analysis → Session Review → Improvement Plan → Optional Re-practice → Progress Tracking.

A first-time user must be able to start a basic interview without uploading a JD. Resume upload should be optional for a generic practice mode, while resume-based personalization is recommended.

## 5. Functional Requirements

### 5.1 Account and Consent
- Support sign-up and authentication.
- Explain what data is stored and why.
- Obtain explicit consent before microphone/camera access.
- Allow users to disable camera use while retaining voice/text practice.
- Allow users to delete their interview history and uploaded documents.
- Provide clear retention/deletion behavior.

### 5.2 Resume Upload and Analysis
**Supported initial formats:** PDF and DOCX.

Extract, where present:
- Skills
- Education
- Projects
- Internships
- Certifications
- Achievements
- Work experience

Output:
- Resume strengths
- Missing or unclear information
- Role relevance observations
- Formatting/ATS observations with evidence
- Actionable improvement suggestions

**Important:** Avoid presenting a fabricated or overly precise "ATS score". If a numeric score is used, it must be tied to a documented rubric and clearly labeled as an estimate.

### 5.3 Job Description Analysis
Extract:
- Required skills
- Preferred skills
- Technical requirements
- Soft-skill requirements
- Experience requirements
- Responsibilities

Create a matching view with:
- Strong match
- Partial match
- Missing/unknown match
- Resume evidence
- Evidence confidence

The system must distinguish between "not present in the resume" and "candidate does not have the skill." Missing evidence is not proof of absence.

### 5.4 Interview Configuration
Interview modes:
- HR
- Behavioral
- Technical
- Project
- Mixed
- Campus placement
- Role-specific

Difficulty:
- Easy
- Medium
- Hard

Duration:
- 10, 20, or 30 minutes

Additional options:
- Voice on/off
- Camera on/off
- Number of questions or approximate interview duration
- Focus areas

### 5.5 Question Generation
Questions should be generated from:
- Resume evidence
- Optional JD requirements
- Target role
- Interview mode
- Difficulty
- Previous weaknesses
- Previously asked questions

Requirements:
- Avoid unnecessary repetition.
- Do not invent resume facts.
- Prefer questions with clear evaluation criteria.
- Maintain a balance of core questions and targeted follow-ups.
- Store question provenance so the system can explain why a question was selected.

### 5.6 Voice Interview
Flow:
User speaks → Speech-to-text → Transcript shown/confirmed → Analysis → AI response → Text-to-speech.

Requirements:
- Show the current question clearly.
- Handle silence, interruptions, and transcription failures gracefully.
- Allow transcript correction.
- Do not penalize candidates for known transcription errors.
- If speech recognition confidence is low, ask the candidate to repeat or edit the transcript.
- Provide a text-only fallback.

### 5.7 Camera Practice
Camera is optional.

Potentially measurable presentation signals:
- Approximate speaking pace
- Long pauses
- Excessive movement
- Framing/visibility issues
- Visible environmental distractions

Camera signals must be presented as practice observations, not judgments about competence or personality.

Do not score:
- Attractiveness
- Skin color
- Gender
- Ethnicity
- Facial appearance
- Accent as a proxy for competence
- Honesty or trustworthiness from eye contact

If a signal is unreliable or unavailable, omit it rather than infer a result.

### 5.8 Adaptive Follow-Up Engine
The system may choose a follow-up based on the current answer.

Examples:
- Vague answer → request a concrete example.
- Incomplete technical answer → ask for the missing concept or reasoning.
- Strong answer → ask a deeper role-relevant follow-up.
- Resume claim → ask for implementation details or measurable impact.

Follow-ups must remain relevant to the configured interview and must not endlessly drill into one topic.

### 5.9 Answer Analysis
Evaluate only dimensions relevant to the question.

Possible dimensions:
- Relevance
- Clarity
- Structure
- Specificity
- Technical correctness/depth
- Conciseness
- Evidence/example quality
- STAR structure where applicable

Avoid using "confidence" as a direct psychological trait. If included, use observable communication indicators such as hedging, excessive pauses, or answer fluency and label them appropriately.

Every evaluation must contain:
- Score or qualitative rating
- Short rationale
- Evidence from the answer/transcript
- Actionable improvement

### 5.10 Scoring Rubric
Scores must be based on a documented rubric rather than arbitrary model judgment.

Default scale: 0–100 per applicable dimension.

Recommended interpretation:
- 90–100: Excellent
- 75–89: Strong
- 60–74: Developing
- 40–59: Needs improvement
- 0–39: Major gap

Scores are practice indicators and must not be presented as objective measurements of employability.

### 5.11 Improve My Answer
For weak answers provide:
- Original answer
- Key issues
- Missing evidence or structure
- Suggested structure
- Example improved answer
- STAR version when applicable

The system must preserve the candidate's real experience. It must never invent employers, projects, metrics, responsibilities, certifications, or achievements.

### 5.12 Session Review
Provide:
- Overall practice score
- Dimension-level results
- Strongest answers
- Priority weaknesses
- Top three improvement actions
- Recommended next practice areas

Do not imply that one session provides a reliable measure of hiring success.

### 5.13 Readiness Indicator
A readiness indicator may be provided only as a practice-progress signal.

It should:
- Be based on a transparent rubric.
- Show the underlying dimensions.
- Show uncertainty/limitations when data is insufficient.
- Avoid false precision.
- Never be described as a probability of getting hired.

For example, use "Practice readiness: Developing" rather than an unsupported "74% chance of success."

### 5.14 Next Interview Engine
Store structured weaknesses and improvement history.

Example:
- Session 1: Technical reasoning — Developing; STAR structure — Needs improvement.
- Session 2: Prioritize technical reasoning and behavioral questions.
- Session 3: Re-test unresolved weaknesses and introduce new role-specific questions.

The engine should balance remediation with fresh questions so sessions do not become repetitive.

### 5.15 Progress Dashboard
Track:
- Session scores
- Dimension-level trends
- Repeated weaknesses
- Resolved weaknesses
- Practice volume
- Recent recommendations

Show trends with enough context to avoid overinterpreting small score changes.

### 5.16 Practice Roadmap
Generate a 7-day or custom plan based on:
- Weakness severity
- Target role
- Upcoming practice goals
- Previous performance
- Available time

Each task should have a clear objective and completion criterion.

### 5.17 Final Report
Include:
- Candidate profile summary
- Resume observations
- JD match observations
- Interview results
- Question-level feedback
- Strengths
- Priority weaknesses
- Improved-answer examples
- Practice recommendations
- Next-session focus
- Progress comparison

Reports should distinguish candidate-provided facts from AI-generated observations.

## 6. Personalization and Memory
Store structured practice history rather than relying only on raw conversation history.

Persist, where consented:
- Resume version/reference
- Target role
- JD reference
- Session metadata
- Questions asked
- Transcript/edited transcript
- Evaluation results
- Weaknesses
- Improvement actions
- Progress trends

When a resume changes, the system must treat the new resume as a new source/version and avoid mixing old and new claims without clear labeling.

## 7. Safety, Fairness, Privacy and Transparency
- Never claim to predict hiring outcomes.
- Never score protected or sensitive characteristics.
- Keep camera analysis optional.
- Explain automated evaluations with evidence.
- Allow transcript correction and re-analysis.
- Clearly label AI-generated feedback.
- Minimize stored personal data.
- Encrypt sensitive data in transit and at rest where applicable.
- Define retention and deletion policies before launch.
- Restrict access to resumes, recordings, transcripts, and reports.
- Obtain consent before recording or storing audio/video.
- Provide a way to delete stored candidate data.
- Log model/version information for important evaluations so results can be audited.

## 8. MVP Scope

### P0 — Required for MVP
1. Authentication
2. Consent and privacy controls
3. Resume upload and parsing
4. Basic resume analysis
5. Optional JD upload and extraction
6. Resume/JD matching
7. Personalized question generation
8. Text-based interview flow
9. Voice interview
10. Adaptive follow-ups
11. Evidence-based answer feedback
12. Transcript editing and re-scoring
13. Session summary
14. Improve My Answer
15. Basic session history

### P1 — Post-MVP
- Camera presentation observations
- Readiness indicator
- Weakness-based next interview
- Progress dashboard
- Session comparison
- Practice roadmap
- PDF report export

### P2 — Future
- Multiple interviewer styles
- Company-specific modes
- Coding interview mode
- Group discussion mode
- Multilingual interviews
- Recruiter/admin dashboard
- Advanced analytics

**MVP principle:** Do not make camera analysis, advanced analytics, or long-term personalization blockers for the first usable release.

## 9. Technical Architecture

### Frontend
Recommended: React/Next.js or an equivalent production web framework.

Responsibilities:
- Authentication
- Resume/JD upload
- Interview UI
- Voice controls
- Optional camera UI
- Feedback and dashboard

### Backend
Recommended: Python/FastAPI or equivalent API service.

Responsibilities:
- Authentication/authorization
- File processing
- Interview orchestration
- Question generation
- Scoring/evaluation orchestration
- Session persistence
- Report generation

### AI Services
Use replaceable service interfaces for:
- LLM question generation
- LLM follow-up generation
- LLM evaluation
- Resume/JD extraction
- Speech-to-text
- Text-to-speech
- Optional computer vision

The architecture must not depend on one model vendor.

### Database
Core entities:
- Users
- Consent records
- Resume versions
- Job descriptions
- Interview configurations
- Sessions
- Questions
- Answers/transcripts
- Evaluation results
- Weaknesses
- Improvement actions
- Progress summaries

### Object Storage
Use controlled storage for uploaded resumes and optional audio/video. Store references and metadata in the database rather than large binary files directly in relational tables.

## 10. Reliability and Quality Requirements
- Graceful fallback when an AI or speech service fails.
- Idempotent session/question operations where practical.
- Preserve the original transcript separately from user-edited transcripts.
- Make evaluation results reproducible enough for debugging by recording model/configuration versions.
- Prevent duplicate question generation during retries.
- Validate uploaded files and enforce size/type limits.
- Provide clear error states instead of silently producing incomplete results.

## 11. Evaluation and Quality Metrics
Product metrics:
- Resume analysis completion rate
- Interview start rate
- Interview completion rate
- Repeat-session rate
- Improvement in rubric scores across comparable sessions
- Weakness resolution rate
- User-reported usefulness

AI quality metrics:
- Question relevance
- Question duplication rate
- Follow-up relevance
- Transcript accuracy
- Evaluation agreement with human reviewers
- Unsupported-claim rate
- Feedback actionability

### Main Success Metric
For users who complete at least two comparable sessions, measure whether targeted rubric dimensions improve between sessions.

Do not treat raw score increase alone as proof of product quality; also monitor question difficulty, rubric consistency, and human-review agreement.

## 12. Acceptance Criteria for MVP
A release is acceptable when:
- A user can complete an interview from start to finish without manual operator support.
- Resume-derived questions cite or reference actual resume evidence.
- The system does not invent candidate experience.
- Transcription errors can be corrected before final scoring.
- Every score has a rationale and answer evidence.
- Follow-ups remain relevant to the interview configuration.
- Users can practice without enabling camera.
- Users can delete their stored practice data.
- Service failures show a recoverable error or fallback.
- Human evaluators judge a predefined sample of questions and feedback as sufficiently relevant and actionable according to an agreed evaluation rubric.

## 13. Risks and Mitigations
| Risk | Mitigation |
|---|---|
| LLM invents resume facts | Ground prompts in extracted evidence; validate claims; show source evidence |
| Inconsistent scoring | Fixed rubric, calibration set, model/version logging, human evaluation |
| Speech transcription errors | Editable transcript, confidence checks, re-analysis |
| Bias in evaluation | Sensitive-attribute exclusions, fairness testing, human audits |
| Camera misinterpretation | Optional feature, conservative observations, no personality/competence inference |
| Privacy exposure | Consent, encryption, access controls, retention/deletion controls |
| Repetitive interviews | Question history and diversity constraints |
| False readiness precision | Rubric-based bands and limitations instead of unsupported probabilities |
| Vendor/API failure | Provider abstraction and graceful fallbacks |
| Scope creep | Strict P0/P1/P2 separation |

## 14. Product Positioning
Do not position the product as simply:
> "AI that conducts interviews."

Position it as:
> "A personalized AI interview training system that analyzes, coaches, and helps candidates improve through repeated practice."

## 15. Final One-Line Description
AI Interview Coach is a personalized AI interview training platform that uses resume and optional job-description intelligence, adaptive practice, voice interviews, evidence-based feedback, and progress tracking to help candidates improve their interview skills over time.
