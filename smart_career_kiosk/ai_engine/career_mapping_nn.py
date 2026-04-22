"""
ai_engine/career_mapping_nn.py
Career Mapping Neural Network (CMNN)
Analyzes user profiles to determine career options, development paths,
and job success probabilities based on labor market trends.
"""

import math
import random
from typing import List, Dict, Tuple
from models.user_profile import UserProfile


# ---------------------------------------------------------------------------
# Simulated career knowledge base
# In production, this would be a trained neural network loaded from a file.
# ---------------------------------------------------------------------------

CAREER_PATHS = {
    "Software Engineer": {
        "required_skills": ["Python", "Java", "JavaScript", "SQL", "Git"],
        "education_boost": {"Bachelor's": 1.0, "Master's": 1.2, "PhD": 1.3},
        "experience_weight": 0.4,
        "base_salary": 95000,
        "growth_rate": 0.22,          # 22% projected 10-yr growth
        "industries": ["Technology", "Finance", "Healthcare"],
    },
    "Data Scientist": {
        "required_skills": ["Python", "Machine Learning", "Statistics", "SQL", "R"],
        "education_boost": {"Bachelor's": 0.9, "Master's": 1.2, "PhD": 1.4},
        "experience_weight": 0.35,
        "base_salary": 105000,
        "growth_rate": 0.35,
        "industries": ["Technology", "Finance", "Research"],
    },
    "Cybersecurity Analyst": {
        "required_skills": ["Networking", "Linux", "Python", "Risk Assessment", "SIEM"],
        "education_boost": {"High School": 0.7, "Bachelor's": 1.0, "Master's": 1.15},
        "experience_weight": 0.45,
        "base_salary": 92000,
        "growth_rate": 0.32,
        "industries": ["Technology", "Government", "Finance"],
    },
    "UX/UI Designer": {
        "required_skills": ["Figma", "User Research", "Prototyping", "CSS", "Wireframing"],
        "education_boost": {"Bachelor's": 1.0, "Master's": 1.1},
        "experience_weight": 0.5,
        "base_salary": 78000,
        "growth_rate": 0.13,
        "industries": ["Technology", "Marketing", "E-commerce"],
    },
    "Project Manager": {
        "required_skills": ["Agile", "Leadership", "Risk Management", "Communication", "MS Project"],
        "education_boost": {"Bachelor's": 1.0, "Master's": 1.15, "MBA": 1.25},
        "experience_weight": 0.6,
        "base_salary": 88000,
        "growth_rate": 0.07,
        "industries": ["Technology", "Construction", "Healthcare", "Finance"],
    },
    "Healthcare Administrator": {
        "required_skills": ["Healthcare Policy", "Budgeting", "Leadership", "EHR Systems", "Compliance"],
        "education_boost": {"Bachelor's": 1.0, "Master's": 1.3},
        "experience_weight": 0.55,
        "base_salary": 82000,
        "growth_rate": 0.28,
        "industries": ["Healthcare"],
    },
    "Financial Analyst": {
        "required_skills": ["Excel", "Financial Modeling", "SQL", "Statistics", "Bloomberg"],
        "education_boost": {"Bachelor's": 1.0, "Master's": 1.2, "CFA": 1.35},
        "experience_weight": 0.45,
        "base_salary": 85000,
        "growth_rate": 0.09,
        "industries": ["Finance", "Banking", "Insurance"],
    },
    "Content Strategist": {
        "required_skills": ["SEO", "Copywriting", "Analytics", "Social Media", "CMS"],
        "education_boost": {"Bachelor's": 1.0, "Master's": 1.1},
        "experience_weight": 0.4,
        "base_salary": 65000,
        "growth_rate": 0.08,
        "industries": ["Marketing", "Media", "E-commerce"],
    },
}

DEVELOPMENT_RESOURCES = {
    "Python": ["Coursera - Python for Everybody", "Real Python (realpython.com)", "Automate the Boring Stuff"],
    "Machine Learning": ["fast.ai", "Coursera - ML Specialization", "Kaggle Learn"],
    "Agile": ["PMI-ACP Certification", "Scrum Alliance Training", "LinkedIn Learning - Agile"],
    "Figma": ["Figma Community Tutorials", "Udemy - UI/UX Design Bootcamp"],
    "SQL": ["Mode Analytics SQL Tutorial", "SQLZoo", "LeetCode Database Problems"],
    "Leadership": ["Harvard ManageMentor", "Dale Carnegie Training", "Coursera - Inspiring Leadership"],
}


class CareerMappingNN:
    """
    Simulated Career Mapping Neural Network.
    
    In a production system this class would load a trained PyTorch / TensorFlow
    model. Here we use a weighted scoring heuristic that mirrors what such a
    model would produce, making the code fully runnable without GPU resources.
    """

    def __init__(self):
        self.career_paths = CAREER_PATHS
        self._warm_up()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict_career_matches(
        self, profile: UserProfile, top_n: int = 5
    ) -> List[Tuple[str, float, Dict]]:
        """
        Return the top_n career matches for a user profile.
        
        Returns:
            List of (career_title, match_score, details_dict)
        """
        scores = {}
        for career, data in self.career_paths.items():
            score = self._score_career(profile, career, data)
            scores[career] = score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

        results = []
        for career, score in ranked:
            data = self.career_paths[career]
            projected_salary = self._project_salary(profile, data)
            skill_gaps = self._identify_skill_gaps(profile, data)
            growth_label = self._growth_label(data["growth_rate"])

            results.append((
                career,
                round(score, 3),
                {
                    "projected_salary": projected_salary,
                    "skill_gaps": skill_gaps,
                    "growth_rate": data["growth_rate"],
                    "growth_label": growth_label,
                    "industries": data["industries"],
                    "development_resources": self._get_resources(skill_gaps),
                },
            ))

        return results

    def success_probability(self, profile: UserProfile, career_title: str) -> float:
        """Return a 0-1 probability that the user will succeed in the given career."""
        if career_title not in self.career_paths:
            return 0.0
        data = self.career_paths[career_title]
        raw = self._score_career(profile, career_title, data)
        # Sigmoid normalisation
        return round(1 / (1 + math.exp(-10 * (raw - 0.5))), 3)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _warm_up(self):
        """Simulate model warm-up (weight loading in production)."""
        _ = [random.random() for _ in range(100)]   # placeholder

    def _score_career(self, profile: UserProfile, career: str, data: dict) -> float:
        """Weighted heuristic scoring — mirrors a neural net forward pass."""
        all_skills = set(s.lower() for s in profile.technical_skills + profile.soft_skills)
        required = set(s.lower() for s in data["required_skills"])

        # Skill overlap score  (0–1)
        if required:
            skill_score = len(all_skills & required) / len(required)
        else:
            skill_score = 0.5

        # Education boost
        edu_boost = data["education_boost"].get(profile.education_level, 0.8)

        # Experience score (log scale, caps at ~20 years)
        exp_score = min(1.0, math.log1p(profile.years_of_experience) / math.log1p(20))

        # Industry alignment bonus
        pref_industry = profile.preferred_industry.lower()
        industry_bonus = 0.1 if any(
            pref_industry in ind.lower() for ind in data["industries"]
        ) else 0.0

        # Weighted combination
        raw_score = (
            skill_score * 0.45
            + exp_score * data["experience_weight"] * 0.35
            + (edu_boost - 0.8) * 0.15
            + industry_bonus
        )

        # Add small noise to simulate stochastic model predictions
        noise = random.gauss(0, 0.01)
        return max(0.0, min(1.0, raw_score + noise))

    def _project_salary(self, profile: UserProfile, data: dict) -> int:
        """Project annual salary based on experience and education."""
        base = data["base_salary"]
        edu_boost = data["education_boost"].get(profile.education_level, 1.0)
        exp_boost = 1 + (profile.years_of_experience * 0.025)   # 2.5% per year
        return int(base * edu_boost * exp_boost)

    def _identify_skill_gaps(self, profile: UserProfile, data: dict) -> List[str]:
        """Return required skills the user currently lacks."""
        user_skills = set(s.lower() for s in profile.technical_skills + profile.soft_skills)
        required = data["required_skills"]
        return [s for s in required if s.lower() not in user_skills]

    def _get_resources(self, skill_gaps: List[str]) -> List[str]:
        """Map skill gaps to learning resources."""
        resources = []
        for skill in skill_gaps[:3]:  # limit to top 3 gaps
            resources.extend(DEVELOPMENT_RESOURCES.get(skill, [f"Search '{skill} tutorial' on Coursera or Udemy"]))
        return resources[:5]

    @staticmethod
    def _growth_label(rate: float) -> str:
        if rate >= 0.25:
            return "Much faster than average"
        if rate >= 0.15:
            return "Faster than average"
        if rate >= 0.05:
            return "Average"
        return "Below average"
