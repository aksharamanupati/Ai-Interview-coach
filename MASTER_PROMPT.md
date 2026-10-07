# AI Interview Coach — Master Specification & Prompt Contract

## 1. Product Vision & Mission
AI Interview Coach is a personalized AI interview training and coaching platform built primarily for college students, freshers, and campus placement candidates.
Rather than acting as an arbitrary grading exam or hiring predictor, the platform functions as an **empathetic, evidence-backed personal coach** that learns from every session, identifies concrete weaknesses, guides answer structuring, and personalizes subsequent interviews based on prior deficits.

## 2. Core Value Proposition & USP
> *"An AI Interview Coach that learns from every interview and automatically adapts the next interview based on the candidate's weaknesses."*

- **Coaching over simple scoring:** Explain the exact why behind any observation.
- **Evidence over unsupported judgments:** Always cite verbatim quotes from the candidate's answers.
- **Practice guidance, not hiring prediction:** Explicitly avoid claiming to predict whether a company will hire the candidate.
- **Transcript correction before final scoring:** Speech-to-text is imperfect; candidates can review and edit their transcript without penalty before evaluations run.
- **Preserve real experience:** "Improve My Answer" must never fabricate unearned achievements, employers, or metrics.
- **Optional camera with ethical guardrails:** Practice presentation signals (pace, pauses, framing) without scoring beauty, race, gender, accent, or personality.

## 3. End-to-End Signature Workflow
```
[1. Profile & Consent]
        │
[2. Resume Upload & Parsing] ──> [ATS / Readability / Skills Observations]
        │
[3. Optional Job Description] ──> [JD vs Resume Coverage Matrix]
        │
[4. Interview Configuration] ──> Mode, Difficulty, Duration, Voice/Camera
        │
[5. Personalized Interview] ──> Role-Grounded Questions with Provenance
        │
[6. Candidate Answer Capture] ──> Voice / Audio Input with Text Fallback
        │
[7. Transcript Review & Edit] ──> Candidate Corrects Mis-transcriptions
        │
[8. Adaptive Follow-Up Engine] ──> Vague/Incomplete Answers Probe Deeper
        │
[9. Rubric Answer Evaluation] ──> Scores + Verbatim Evidence + Actionable Tips
        │
[10. Improve My Answer] ──> Structured Rewrites (STAR format) Preserving Facts
        │
[11. Session Review & Readiness] ──> Multi-Dimensional Scorecard & Next Steps
        │
[12. Next Interview Engine] ──> Next Session Prioritizes Identified Weaknesses
        │
[13. Progress Tracking & Roadmap] ──> Session N vs N+1 Comparison & 7-Day Plan
```

## 4. Engineering & Safety Guardrails
1. **Zero Key Exposure:** Never leak API keys in code, stack traces, or UI.
2. **Offline / Resilient Execution:** Provide a fully offline-capable, deterministic NLP coach provider with zero external dependencies, while supporting optional Gemini API integration.
3. **Pluggable Architecture:** Decouple parsing, question generation, audio STT/TTS, and scoring.
4. **Data Privacy:** Local storage for session history with a one-click "Clear History" option.
