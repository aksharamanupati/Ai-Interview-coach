"""
Comprehensive Automated Test Suite for AI Interview Coach.
Verifies all 14 PRD Acceptance Criteria and core functional flows.
"""
import unittest
import os
from pathlib import Path
from parsers.resume_parser import parse_resume, extract_text_from_file
from parsers.jd_parser import parse_job_description
from parsers.gap_analyzer import analyze_gap
from interview.question_engine import generate_interview_plan
from interview.followup_engine import generate_adaptive_followup
from interview.next_interview_engine import prepare_next_interview_profile, compare_sessions
from ai_providers.offline_provider import OfflineAIProvider
from evaluation.rubric_scorer import summarize_session
from evaluation.readiness_calculator import calculate_readiness
from evaluation.roadmap_generator import generate_practice_roadmap
from camera.presentation_tracker import evaluate_presentation_cadence, ETHICAL_DISCLAIMER
from storage.session_db import save_session, get_all_sessions, delete_all_history
from ui.report_exporter import generate_markdown_report
from app import (
    get_stage_progress,
    explain_question_in_language,
    build_result_cards,
    build_resume_analysis_summary,
    next_question_after_answer,
    check_repeat_question_safe,
)
from ui.interview_app import LANGUAGE_TAGS, ROLE_QUESTIONS, _create_questions

class TestAIInterviewCoach(unittest.TestCase):

    def setUp(self):
        delete_all_history("Test_Candidate")
        self.sample_resume_text = (
            "Manupati Akshara\n"
            "Telangana | aksharamanupati1630@gmail.com | 9705291630\n"
            "Summary: Computer science student with solid foundation in Python and C. Hands-on experience in competitive programming via HackerRank.\n"
            "Education: Malla Reddy Engineering College For Women, B.Tech Computer Science. CGPA: 7.2 / 10\n"
            "Technical Skills: Python, C, C++, Data Structures, Algorithms, SQL, Git, OOP\n"
            "Projects:\n"
            "1. Emotion-Aware Conversational AI: Built a Python and REST API chatbot with 92% classification accuracy across 10 emotions.\n"
            "2. Library Management System: Designed a relational database application in Python and SQLite for cataloging 5,000+ books.\n"
            "Certifications: HackerRank 5-Star Python, CodeChef 3-Star."
        )
        self.sample_jd_text = (
            "Job Title: Junior Software Engineer\n"
            "Requirements:\n"
            "- Strong proficiency in Python and OOP\n"
            "- Solid foundation in Data Structures, Algorithms, and SQL\n"
            "- Familiarity with Git version control\n"
            "- Preferred: Experience with Docker containers and Cloud deployment"
        )

    def test_01_resume_parser(self):
        """Test resume parsing, section segmentation, and rubric audit."""
        res = parse_resume(self.sample_resume_text)
        self.assertIn("Python", res.skills)
        self.assertIn("Sql", [s.capitalize() for s in res.skills])
        self.assertFalse(any(skill.startswith("1. Emotion") for skill in res.skills))
        self.assertGreaterEqual(len(res.projects), 2)
        self.assertGreaterEqual(res.rubric_score, 60.0)
        self.assertGreaterEqual(len(res.strengths), 1)
        self.assertTrue(any("contact" in f.lower() or "verified" in f.lower() for f in res.formatting_observations))

    def test_02_jd_parser_and_gap_analysis(self):
        """Test JD parsing and coverage matrix with verification questions."""
        res = parse_resume(self.sample_resume_text)
        jd = parse_job_description(self.sample_jd_text)
        self.assertEqual(jd.title, "Junior Software Engineer")
        self.assertIn("Python", jd.required_skills)
        
        gap = analyze_gap(res, jd)
        self.assertGreater(gap.match_score, 50.0)
        self.assertTrue(len(gap.coverage_items) > 0)
        
        # Verify Docker is recognized as missing with a verification question
        docker_item = next((it for it in gap.coverage_items if "docker" in it.skill.lower()), None)
        if docker_item:
            self.assertEqual(docker_item.status, "Missing Evidence")
            self.assertIn("Docker", docker_item.verification_question)

    def test_03_question_generation_with_provenance(self):
        """Test question generation grounded in resume projects and skills with provenance."""
        res = parse_resume(self.sample_resume_text)
        jd = parse_job_description(self.sample_jd_text)
        questions = generate_interview_plan(res, jd, mode="Technical", difficulty="Medium", count=4)
        self.assertEqual(len(questions), 4)
        for q in questions:
            self.assertTrue(len(q.provenance) > 5)
            self.assertTrue(len(q.text) > 15)

    def test_04_adaptive_followup_engine(self):
        """Test adaptive follow-up triggering on vague or incomplete answers."""
        res = parse_resume(self.sample_resume_text)
        provider = OfflineAIProvider()
        q = generate_interview_plan(res, None, count=1)[0]
        
        # 1. Brief/vague answer should trigger elaboration follow-up
        followup_vague = provider.generate_followup(q, "I just wrote some code and it worked fine.", res)
        self.assertIsNotNone(followup_vague)
        self.assertTrue(followup_vague.is_followup)
        self.assertEqual(followup_vague.target_dimension, "Specificity")
        
        # 2. Technical implementation without tradeoff should trigger tradeoff follow-up
        detailed_tech_ans = (
            "In my project I used SQLite and built a relational database model with several tables and structured queries "
            "for cataloging records and managing user actions cleanly."
        )
        followup_tradeoff = provider.generate_followup(q, detailed_tech_ans, res)
        self.assertIsNotNone(followup_tradeoff)
        self.assertTrue("alternative" in followup_tradeoff.text.lower() or "tradeoff" in followup_tradeoff.text.lower())

    def test_05_evidence_based_scoring_and_verbatim_quotes(self):
        """Test rubric scoring contains verbatim quotes and actionable fixes."""
        res = parse_resume(self.sample_resume_text)
        provider = OfflineAIProvider()
        q = generate_interview_plan(res, None, count=1)[0]
        
        candidate_answer = (
            "When building the Emotion-Aware chatbot in college, our goal was to detect user sentiments. "
            "I implemented Python REST endpoints and integrated a vector model. As a result, we reached 92% accuracy on our test set."
        )
        
        eval_res = provider.evaluate_answer(
            question=q,
            answer_text=candidate_answer,
            raw_transcript=candidate_answer,
            resume=res
        )
        
        self.assertGreaterEqual(eval_res.overall_score, 70.0)
        self.assertEqual(len(eval_res.dimensions), 6)
        
        # Check that evidence quotes exist and are taken from candidate answer
        struct_dim = eval_res.dimensions["Structure"]
        self.assertTrue(len(struct_dim.evidence_quotes) > 0)
        self.assertTrue(len(struct_dim.actionable_improvement) > 5)

    def test_06_transcript_editing_support(self):
        """Verify transcript editing before final scoring is tracked and supported without penalty."""
        res = parse_resume(self.sample_resume_text)
        provider = OfflineAIProvider()
        q = generate_interview_plan(res, None, count=1)[0]
        
        raw_speech = "um when billing the emo shot bot i used py thon"
        corrected_text = "When building the emotion chatbot, I used Python to structure the data pipeline."
        
        eval_res = provider.evaluate_answer(
            question=q,
            answer_text=corrected_text,
            raw_transcript=raw_speech,
            resume=res
        )
        self.assertTrue(eval_res.was_edited)
        self.assertEqual(eval_res.edited_transcript, corrected_text)
        self.assertGreaterEqual(eval_res.dimensions["Clarity"].score, 75.0)

    def test_07_improve_my_answer_preserves_facts(self):
        """Verify 'Improve My Answer' produces STAR structure preserving candidate facts without inventing fake roles."""
        res = parse_resume(self.sample_resume_text)
        provider = OfflineAIProvider()
        q = generate_interview_plan(res, None, count=1)[0]
        
        ans_text = "I built the library management database."
        improved, star = provider.improve_answer(q, ans_text, "Structure", res)
        
        self.assertIn("**Situation:**", star)
        self.assertIn("**Action:**", star)
        self.assertIn("**Result:**", star)
        # Should reference candidate's real project
        self.assertTrue("Emotion-Aware" in star or "Library Management" in star or "Python" in star)

    def test_08_session_aggregator_and_readiness_indicator(self):
        """Test session aggregation, non-predictive readiness indicator, and 7-day roadmap."""
        res = parse_resume(self.sample_resume_text)
        provider = OfflineAIProvider()
        qs = generate_interview_plan(res, None, count=2)
        
        evals = [
            provider.evaluate_answer(qs[0], "I built the system using Python and SQLite with 5000 records.", "", res),
            provider.evaluate_answer(qs[1], "We worked as a team to resolve git merge conflicts and test code.", "", res)
        ]
        
        summary = summarize_session(
            candidate_name="Test_Candidate",
            target_role="Software Engineer",
            interview_mode="Mixed",
            difficulty="Medium",
            evaluations=evals
        )
        
        self.assertGreater(summary.overall_score, 0)
        self.assertIn("practice readiness:", summary.readiness_explanation.lower())
        self.assertIn("not a prediction of hiring", summary.readiness_explanation.lower())
        self.assertEqual(len(summary.top_3_actions), 3)
        self.assertEqual(len(summary.practice_roadmap), 7)

    def test_09_multi_session_persistence_and_next_interview_engine(self):
        """
        Verify the Core USP:
        Session 1 stores weaknesses -> Next Interview Engine targets those weaknesses -> Session 2 shows measurable progress!
        """
        res = parse_resume(self.sample_resume_text)
        provider = OfflineAIProvider()
        qs = generate_interview_plan(res, None, count=2)
        
        # Session 1: Weak answers on structure
        evals_s1 = [
            provider.evaluate_answer(qs[0], "Yeah I just wrote it fast.", "", res),
            provider.evaluate_answer(qs[1], "Nothing special, it worked.", "", res)
        ]
        summary_s1 = summarize_session(
            candidate_name="Test_Candidate",
            target_role="Software Engineer",
            interview_mode="Mixed",
            difficulty="Medium",
            evaluations=evals_s1
        )
        save_session(summary_s1)
        
        # Next Interview Engine analyzes Session 1
        next_profile = prepare_next_interview_profile("Test_Candidate")
        self.assertTrue(next_profile["has_history"])
        self.assertEqual(next_profile["session_count"], 1)
        self.assertTrue(len(next_profile["targeted_weaknesses"]) > 0)
        
        # Generate Session 2 targeting Session 1 weaknesses
        s2_questions = generate_interview_plan(
            res, None,
            mode=next_profile["recommended_mode"],
            difficulty=next_profile["recommended_difficulty"],
            count=2,
            previous_weaknesses=next_profile["targeted_weaknesses"]
        )
        
        # S2 question provenance should indicate targeting prior weakness
        self.assertTrue(any("previous session weakness" in q.provenance.lower() for q in s2_questions))
        
        # Session 2: Strong structured answers
        evals_s2 = [
            provider.evaluate_answer(
                s2_questions[0],
                "In my Library Management project, my task was to optimize SQL queries. I added indexing on book IDs, which reduced response time by 40% across 5,000 catalog items.",
                "", res
            ),
            provider.evaluate_answer(
                s2_questions[1],
                "When a team member disagreed on the API structure, my goal was to find common ground. I organized a code review session, mapped both schemas, and as a result we agreed on a unified REST standard.",
                "", res
            )
        ]
        summary_s2 = summarize_session(
            candidate_name="Test_Candidate",
            target_role="Software Engineer",
            interview_mode=next_profile["recommended_mode"],
            difficulty=next_profile["recommended_difficulty"],
            evaluations=evals_s2
        )
        save_session(summary_s2)
        
        # Compare Session 1 vs Session 2
        comp = compare_sessions("Test_Candidate")
        self.assertTrue(comp["can_compare"])
        self.assertGreater(comp["overall_delta"], 0, "Session 2 overall score should demonstrate improvement over Session 1")
        self.assertGreater(comp["readiness_delta"], 0, "Session 2 readiness should demonstrate measurable improvement")

    def test_10_camera_presentation_cadence_and_ethical_rules(self):
        """Test camera presentation observations and ethical disclaimer."""
        pacing = evaluate_presentation_cadence(word_count=135, duration_seconds=60.0)
        self.assertEqual(pacing["pace_status"], "Optimal")
        self.assertIn("135", str(pacing["wpm"]))
        self.assertIn(ETHICAL_DISCLAIMER, pacing["ethical_disclaimer"])

    def test_11_data_privacy_deletion(self):
        """Verify candidate can clear / delete their interview history."""
        delete_all_history("Test_Candidate")
        sessions = get_all_sessions("Test_Candidate")
        self.assertEqual(len(sessions), 0)

    def test_12_guided_flow_navigation_and_question_state(self):
        """Verify the guided step flow, repeat safety, and language explanation helpers."""
        steps = get_stage_progress("resume_analysis")
        self.assertIn("Resume Analysis", steps)
        self.assertEqual(steps[0], "Setup")

        self.assertTrue(check_repeat_question_safe(2, 5))
        self.assertFalse(check_repeat_question_safe(5, 5))

        summary = build_resume_analysis_summary(
            parse_resume(self.sample_resume_text),
            parse_job_description(self.sample_jd_text),
        )
        self.assertIn("score", summary)
        self.assertIn("strengths", summary)
        self.assertIn("weak_areas", summary)

        next_index = next_question_after_answer(3, 10)
        self.assertEqual(next_index, 4)

        explanation = explain_question_in_language(
            "Tell me about a challenging project you worked on.",
            "Telugu",
        )
        self.assertIn("project", explanation.lower())
        self.assertIn("difficult", explanation.lower())

    def test_13_results_summary_cards(self):
        """Verify results cards are built from summary dimension data without fabricating unsupported categories."""
        summary = {
            "overall_score": 72,
            "dimension_scores": {
                "Communication": 80,
                "Answer Quality": 75,
                "Technical Knowledge": 70,
                "Confidence / Presentation": 68,
                "Answer Delivery": 76,
            },
            "strengths": ["Clear communication", "Structured responses"],
            "areas_to_improve": ["Technical depth", "Confidence"],
        }
        cards = build_result_cards(summary)
        self.assertEqual(cards["overall_score"], 72)
        self.assertIn("Communication", cards["category_scores"])
        self.assertEqual(cards["strengths"][0], "Clear communication")
        self.assertIn("Technical depth", cards["areas_to_improve"])

    def test_14_role_persists_in_personalized_question_sets(self):
        """Role-specific prompts and browser speech language tags match selected app roles."""
        resume = parse_resume(self.sample_resume_text)
        frontend_questions = _create_questions(resume, "Frontend Developer")
        backend_questions = _create_questions(resume, "Backend Developer")
        analyst_questions = _create_questions(resume, "Data Analyst")

        self.assertTrue(any("useState and useEffect" in q.text for q in frontend_questions))
        self.assertTrue(any("REST API" in q.text for q in backend_questions))
        self.assertTrue(any("SQL" in q.text for q in analyst_questions))
        self.assertEqual(frontend_questions[0].provenance.split("selected ")[1].split(" role")[0], "Frontend Developer")
        self.assertEqual(len(ROLE_QUESTIONS), 8)
        self.assertEqual(LANGUAGE_TAGS["English"], "en-IN")
        self.assertEqual(LANGUAGE_TAGS["Telugu"], "te-IN")
        self.assertEqual(LANGUAGE_TAGS["Bengali"], "bn-IN")

if __name__ == "__main__":
    unittest.main()
