"""
models/user_profile.py
Defines the UserProfile data model used across the kiosk system.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UserProfile:
    """Represents a job seeker's complete profile."""

    # Personal Info
    name: str = ""
    age: int = 0
    location: str = ""

    # Education
    education_level: str = ""          # e.g., "High School", "Bachelor's", "Master's"
    field_of_study: str = ""

    # Experience
    years_of_experience: int = 0
    previous_roles: List[str] = field(default_factory=list)

    # Skills
    technical_skills: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)

    # Preferences
    preferred_industry: str = ""
    preferred_work_type: str = ""      # "Remote", "On-site", "Hybrid"
    salary_expectation: int = 0        # Annual, in USD
    relocation_willing: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "age": self.age,
            "location": self.location,
            "education_level": self.education_level,
            "field_of_study": self.field_of_study,
            "years_of_experience": self.years_of_experience,
            "previous_roles": self.previous_roles,
            "technical_skills": self.technical_skills,
            "soft_skills": self.soft_skills,
            "preferred_industry": self.preferred_industry,
            "preferred_work_type": self.preferred_work_type,
            "salary_expectation": self.salary_expectation,
            "relocation_willing": self.relocation_willing,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        return cls(**data)
