"""
models/job_listing.py
Defines the JobListing data model parsed from external job boards and APIs.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class JobListing:
    """Represents a job posting fetched from external sources."""

    job_id: str
    title: str
    company: str
    location: str
    description: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    salary_min: int = 0
    salary_max: int = 0
    work_type: str = "On-site"        # "Remote", "On-site", "Hybrid"
    industry: str = ""
    posted_date: Optional[datetime] = None
    apply_url: str = ""
    match_score: float = 0.0          # Set by the AI matching engine

    def salary_display(self) -> str:
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} – ${self.salary_max:,}/yr"
        elif self.salary_min:
            return f"From ${self.salary_min:,}/yr"
        return "Salary not disclosed"

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "work_type": self.work_type,
            "industry": self.industry,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "apply_url": self.apply_url,
            "match_score": self.match_score,
        }
