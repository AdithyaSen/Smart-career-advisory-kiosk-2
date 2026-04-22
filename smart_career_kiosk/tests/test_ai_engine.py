"""
tests/test_ai_engine.py
Unit tests for the Career Mapping Neural Network and Recommendation Engine.
Run with: python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from models.user_profile import UserProfile
from models.job_listing import JobListing
from ai_engine.career_mapping_nn import CareerMappingNN
from ai_engine.nlp_job_parser import NLPJobParser
from ai_engine.recommendation_engine import RecommendationEngine


def _sample_profile(**kwargs) -> UserProfile:
    defaults = dict(
        name="Jane Doe",
        age=28,
        location="San Francisco, CA",
        education_level="Bachelor's",
        field_of_study="Computer Science",
        years_of_experience=4,
        previous_roles=["Junior Developer", "Software Engineer"],
        technical_skills=["Python", "SQL", "Machine Learning", "Git"],
        soft_skills=["Leadership", "Communication"],
        preferred_industry="Technology",
        preferred_work_type="Remote",
        salary_expectation=110000,
        relocation_willing=False,
    )
    defaults.update(kwargs)
    return UserProfile(**defaults)


class TestCareerMappingNN(unittest.TestCase):

    def setUp(self):
        self.cmnn = CareerMappingNN()
        self.profile = _sample_profile()

    def test_returns_correct_number_of_matches(self):
        matches = self.cmnn.predict_career_matches(self.profile, top_n=3)
        self.assertEqual(len(matches), 3)

    def test_scores_between_zero_and_one(self):
        matches = self.cmnn.predict_career_matches(self.profile)
        for _, score, _ in matches:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_results_are_ranked_descending(self):
        matches = self.cmnn.predict_career_matches(self.profile)
        scores = [s for _, s, _ in matches]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_details_contain_expected_keys(self):
        matches = self.cmnn.predict_career_matches(self.profile, top_n=1)
        _, _, details = matches[0]
        for key in ("projected_salary", "skill_gaps", "growth_label", "industries"):
            self.assertIn(key, details)

    def test_success_probability_known_career(self):
        prob = self.cmnn.success_probability(self.profile, "Data Scientist")
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)

    def test_success_probability_unknown_career(self):
        prob = self.cmnn.success_probability(self.profile, "Astronaut")
        self.assertEqual(prob, 0.0)

    def test_projected_salary_positive(self):
        matches = self.cmnn.predict_career_matches(self.profile, top_n=1)
        _, _, details = matches[0]
        self.assertGreater(details["projected_salary"], 0)

    def test_strong_skill_match_scores_higher(self):
        weak_profile = _sample_profile(technical_skills=[], soft_skills=[])
        strong = self.cmnn.predict_career_matches(self.profile, top_n=1)[0][1]
        weak   = self.cmnn.predict_career_matches(weak_profile, top_n=1)[0][1]
        self.assertGreater(strong, weak)


class TestNLPJobParser(unittest.TestCase):

    def setUp(self):
        self.parser = NLPJobParser()
        self.profile = _sample_profile()

    def test_fetch_returns_job_listings(self):
        jobs = self.parser.fetch_and_parse_jobs()
        self.assertGreater(len(jobs), 0)
        self.assertIsInstance(jobs[0], JobListing)

    def test_listing_has_required_fields(self):
        jobs = self.parser.fetch_and_parse_jobs(limit=1)
        job = jobs[0]
        self.assertTrue(job.title)
        self.assertTrue(job.company)
        self.assertIsNotNone(job.salary_min)

    def test_match_returns_top_n(self):
        jobs = self.parser.fetch_and_parse_jobs()
        matched = self.parser.match_jobs_to_profile(self.profile, jobs, top_n=3)
        self.assertEqual(len(matched), 3)

    def test_match_scores_between_zero_and_one(self):
        jobs = self.parser.fetch_and_parse_jobs()
        matched = self.parser.match_jobs_to_profile(self.profile, jobs)
        for job in matched:
            self.assertGreaterEqual(job.match_score, 0.0)
            self.assertLessEqual(job.match_score, 1.0)

    def test_skill_extraction(self):
        text = "We need a Python developer with SQL and Machine Learning experience."
        skills = self.parser.extract_skills_from_text(text)
        self.assertIn("Python", skills)

    def test_salary_display(self):
        job = JobListing(
            job_id="001", title="Dev", company="X", location="NY",
            description="", salary_min=80000, salary_max=120000
        )
        self.assertIn("$80,000", job.salary_display())

    def test_query_filter(self):
        jobs = self.parser.fetch_and_parse_jobs(query="Data")
        for job in jobs:
            text = (job.title + job.industry).lower()
            self.assertIn("data", text)


class TestRecommendationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RecommendationEngine()
        self.profile = _sample_profile()

    def test_report_has_expected_keys(self):
        report = self.engine.generate_report(self.profile)
        for key in ("career_matches", "job_matches", "skill_gaps",
                    "salary_scenarios", "user_name", "top_career"):
            self.assertIn(key, report)

    def test_salary_scenarios_non_zero(self):
        report = self.engine.generate_report(self.profile)
        for k, v in report["salary_scenarios"].items():
            self.assertTrue(v.startswith("$"), f"{k} scenario missing $: {v}")

    def test_career_matches_count(self):
        report = self.engine.generate_report(self.profile)
        self.assertEqual(len(report["career_matches"]), 5)

    def test_user_name_in_report(self):
        report = self.engine.generate_report(self.profile)
        self.assertEqual(report["user_name"], "Jane Doe")

    def test_quick_match(self):
        quick = self.engine.quick_match(self.profile, top_n=2)
        self.assertEqual(len(quick), 2)
        for item in quick:
            self.assertIn("career", item)
            self.assertIn("score", item)


if __name__ == "__main__":
    unittest.main(verbosity=2)
