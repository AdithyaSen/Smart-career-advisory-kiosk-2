"""
ai_engine/nlp_job_parser.py
NLP Job Parsing Engine
Continuously collects and processes job postings from various sources,
extracting structured data via Natural Language Processing.
"""

import re
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Optional
from models.job_listing import JobListing
from models.user_profile import UserProfile


# ---------------------------------------------------------------------------
# Simulated job board data (replaces live API calls for demo purposes)
# ---------------------------------------------------------------------------

_SAMPLE_JOB_POOL = [
    {
        "title": "Senior Software Engineer",
        "company": "TechNova Inc.",
        "location": "San Francisco, CA",
        "description": "Build scalable backend systems in Python and Go. Work with ML teams to integrate AI pipelines.",
        "skills": ["Python", "Go", "SQL", "Docker", "Kubernetes", "Git"],
        "salary_min": 130000, "salary_max": 170000,
        "work_type": "Hybrid", "industry": "Technology",
    },
    {
        "title": "Data Scientist – Healthcare Analytics",
        "company": "MedInsight Solutions",
        "location": "Remote",
        "description": "Analyze patient datasets, build predictive models for hospital readmission risk.",
        "skills": ["Python", "R", "Machine Learning", "Statistics", "SQL"],
        "salary_min": 115000, "salary_max": 145000,
        "work_type": "Remote", "industry": "Healthcare",
    },
    {
        "title": "Cybersecurity Analyst II",
        "company": "SecureNet Corp",
        "location": "Washington, D.C.",
        "description": "Monitor SIEM tools, conduct vulnerability assessments, respond to incidents.",
        "skills": ["Networking", "Linux", "SIEM", "Python", "Risk Assessment"],
        "salary_min": 90000, "salary_max": 115000,
        "work_type": "On-site", "industry": "Government",
    },
    {
        "title": "UX Designer – Mobile Applications",
        "company": "AppCraft Studio",
        "location": "Austin, TX",
        "description": "Lead user research, create wireframes and high-fidelity prototypes for iOS/Android.",
        "skills": ["Figma", "User Research", "Prototyping", "Wireframing"],
        "salary_min": 80000, "salary_max": 105000,
        "work_type": "Hybrid", "industry": "Technology",
    },
    {
        "title": "Agile Project Manager",
        "company": "BuildRight Consulting",
        "location": "Chicago, IL",
        "description": "Manage cross-functional software delivery teams using Scrum and Kanban frameworks.",
        "skills": ["Agile", "Leadership", "Risk Management", "Communication", "Jira"],
        "salary_min": 88000, "salary_max": 118000,
        "work_type": "Hybrid", "industry": "Technology",
    },
    {
        "title": "Financial Analyst – FP&A",
        "company": "Vertex Capital Group",
        "location": "New York, NY",
        "description": "Build financial models, perform variance analysis, support quarterly forecasting.",
        "skills": ["Excel", "Financial Modeling", "SQL", "Statistics", "Bloomberg"],
        "salary_min": 85000, "salary_max": 110000,
        "work_type": "On-site", "industry": "Finance",
    },
    {
        "title": "Healthcare Administrator",
        "company": "Sunrise Medical Center",
        "location": "Houston, TX",
        "description": "Oversee clinic operations, manage budgets, ensure regulatory compliance.",
        "skills": ["Healthcare Policy", "Budgeting", "Leadership", "EHR Systems", "Compliance"],
        "salary_min": 78000, "salary_max": 100000,
        "work_type": "On-site", "industry": "Healthcare",
    },
    {
        "title": "Junior Data Scientist",
        "company": "DataStream Analytics",
        "location": "Remote",
        "description": "Assist senior scientists in building ML pipelines and data visualization dashboards.",
        "skills": ["Python", "Machine Learning", "SQL"],
        "salary_min": 75000, "salary_max": 95000,
        "work_type": "Remote", "industry": "Technology",
    },
    {
        "title": "Content Strategist",
        "company": "BrandVoice Agency",
        "location": "Los Angeles, CA",
        "description": "Develop SEO content strategies, manage editorial calendars, analyze performance metrics.",
        "skills": ["SEO", "Copywriting", "Analytics", "Social Media", "CMS"],
        "salary_min": 62000, "salary_max": 82000,
        "work_type": "Hybrid", "industry": "Marketing",
    },
    {
        "title": "Full-Stack Software Engineer",
        "company": "Nexgen Startups",
        "location": "Remote",
        "description": "Design and build web applications using React, Node.js, and PostgreSQL.",
        "skills": ["JavaScript", "React", "Node.js", "SQL", "Git", "Python"],
        "salary_min": 100000, "salary_max": 135000,
        "work_type": "Remote", "industry": "Technology",
    },
]


# ---------------------------------------------------------------------------
# Skill extraction patterns (simplified NER rules)
# ---------------------------------------------------------------------------

SKILL_PATTERNS = [
    r"\bPython\b", r"\bJava\b", r"\bJavaScript\b", r"\bSQL\b", r"\bR\b",
    r"\bGo\b", r"\bDocker\b", r"\bKubernetes\b", r"\bGit\b",
    r"\bMachine Learning\b", r"\bStatistics\b", r"\bSEO\b",
    r"\bFigma\b", r"\bAgile\b", r"\bLeadership\b",
]


class NLPJobParser:
    """
    NLP-based job description parser.
    
    Responsibilities:
    - Fetch (simulated) job listings from external sources.
    - Extract structured fields (skills, salary, work type) from raw text.
    - Match and rank listings against a user profile.
    """

    def __init__(self):
        self._job_pool = _SAMPLE_JOB_POOL

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_and_parse_jobs(self, query: str = "", limit: int = 20) -> List[JobListing]:
        """
        Simulate fetching jobs from job boards (e.g., LinkedIn, Indeed, BLS).
        In production this would make authenticated API calls.
        """
        jobs = []
        pool = self._job_pool if not query else [
            j for j in self._job_pool
            if query.lower() in j["title"].lower()
            or query.lower() in j["industry"].lower()
        ]

        for raw in pool[:limit]:
            listing = self._parse_raw_job(raw)
            jobs.append(listing)

        return jobs

    def match_jobs_to_profile(
        self, profile: UserProfile, jobs: List[JobListing], top_n: int = 5
    ) -> List[JobListing]:
        """
        Score each job against the user profile and return the top_n matches.
        """
        user_skills = set(s.lower() for s in profile.technical_skills + profile.soft_skills)

        for job in jobs:
            job.match_score = self._compute_match_score(profile, job, user_skills)

        ranked = sorted(jobs, key=lambda j: j.match_score, reverse=True)
        return ranked[:top_n]

    def extract_skills_from_text(self, text: str) -> List[str]:
        """Use regex patterns to extract skills from raw job description text."""
        found = []
        for pattern in SKILL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                found.append(re.search(pattern, text, re.IGNORECASE).group())
        return list(set(found))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_raw_job(self, raw: dict) -> JobListing:
        """Convert a raw dictionary into a structured JobListing."""
        posted = datetime.now() - timedelta(days=random.randint(0, 14))
        return JobListing(
            job_id=str(uuid.uuid4())[:8],
            title=raw["title"],
            company=raw["company"],
            location=raw["location"],
            description=raw["description"],
            required_skills=raw.get("skills", []),
            salary_min=raw.get("salary_min", 0),
            salary_max=raw.get("salary_max", 0),
            work_type=raw.get("work_type", "On-site"),
            industry=raw.get("industry", ""),
            posted_date=posted,
            apply_url=f"https://careers.example.com/{raw['company'].replace(' ', '-').lower()}",
        )

    def _compute_match_score(
        self, profile: UserProfile, job: JobListing, user_skills: set
    ) -> float:
        """
        Multi-factor matching score (0.0 – 1.0):
        - Skill overlap (50%)
        - Salary alignment (20%)
        - Work-type preference (15%)
        - Industry alignment (15%)
        """
        # Skill overlap
        required = set(s.lower() for s in job.required_skills)
        skill_score = len(user_skills & required) / max(len(required), 1)

        # Salary alignment
        if profile.salary_expectation and job.salary_max:
            diff_ratio = abs(profile.salary_expectation - job.salary_max) / job.salary_max
            salary_score = max(0.0, 1.0 - diff_ratio)
        else:
            salary_score = 0.5

        # Work-type preference
        work_score = 1.0 if job.work_type == profile.preferred_work_type else 0.3

        # Industry alignment
        industry_score = (
            1.0 if profile.preferred_industry.lower() == job.industry.lower() else 0.4
        )

        return round(
            skill_score * 0.50
            + salary_score * 0.20
            + work_score * 0.15
            + industry_score * 0.15,
            3,
        )
