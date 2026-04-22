"""
ai_engine/recommendation_engine.py
Recommendation Engine
Orchestrates the CMNN and NLP Job Parser to produce a unified
career advisory report for the user.
"""

from typing import List, Dict, Any
from models.user_profile import UserProfile
from models.job_listing import JobListing
from ai_engine.career_mapping_nn import CareerMappingNN
from ai_engine.nlp_job_parser import NLPJobParser


class RecommendationEngine:
    """
    Central orchestrator that merges career predictions with live job matches
    to produce personalised, multi-scenario career advice.
    """

    def __init__(self):
        self.cmnn = CareerMappingNN()
        self.nlp_parser = NLPJobParser()

    def generate_report(self, profile: UserProfile) -> Dict[str, Any]:
        """
        Generate a full career advisory report for the given user profile.

        Returns a structured dictionary with:
          - career_matches   : Top career path recommendations
          - job_matches      : Top matching open positions
          - skill_gaps       : Skills to develop
          - learning_paths   : Resources for each gap
          - salary_scenarios : Low / median / high salary projections
        """
        # 1. Career path analysis via CMNN
        career_matches = self.cmnn.predict_career_matches(profile, top_n=5)

        # 2. Live job matching via NLP parser
        all_jobs = self.nlp_parser.fetch_and_parse_jobs(limit=20)
        job_matches = self.nlp_parser.match_jobs_to_profile(profile, all_jobs, top_n=5)

        # 3. Aggregate skill gaps across top 3 career recommendations
        all_gaps = []
        learning_paths = {}
        for career, score, details in career_matches[:3]:
            gaps = details["skill_gaps"]
            for g in gaps:
                if g not in all_gaps:
                    all_gaps.append(g)
            learning_paths.update(
                {career: details["development_resources"]}
            )

        # 4. Salary scenarios for top career match
        top_career, _, top_details = career_matches[0]
        base_sal = top_details["projected_salary"]
        salary_scenarios = {
            "conservative": int(base_sal * 0.85),
            "median":       base_sal,
            "optimistic":   int(base_sal * 1.20),
        }

        return {
            "user_name": profile.name,
            "career_matches": [
                {
                    "title": c,
                    "match_score": f"{s * 100:.0f}%",
                    "projected_salary": f"${d['projected_salary']:,}",
                    "growth_label": d["growth_label"],
                    "skill_gaps": d["skill_gaps"],
                    "industries": d["industries"],
                }
                for c, s, d in career_matches
            ],
            "job_matches": [
                {
                    "title": j.title,
                    "company": j.company,
                    "location": j.location,
                    "salary": j.salary_display(),
                    "work_type": j.work_type,
                    "match_score": f"{j.match_score * 100:.0f}%",
                    "apply_url": j.apply_url,
                }
                for j in job_matches
            ],
            "skill_gaps": all_gaps[:8],
            "learning_paths": learning_paths,
            "salary_scenarios": {
                k: f"${v:,}" for k, v in salary_scenarios.items()
            },
            "top_career": top_career,
        }

    def quick_match(self, profile: UserProfile, top_n: int = 3) -> List[Dict]:
        """Lightweight version for kiosk idle-mode quick demo."""
        matches = self.cmnn.predict_career_matches(profile, top_n=top_n)
        return [
            {"career": c, "score": f"{s * 100:.0f}%"}
            for c, s, _ in matches
        ]
