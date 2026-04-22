"""
ui/kiosk_interface.py
Kiosk Touchscreen Interface (CLI simulation)
Provides an interactive terminal-based UI that mirrors the touchscreen flow
of the physical kiosk. In a production deployment this would be replaced by
a full-screen Tkinter / PyQt / web-based interface.
"""

import os
import time
from typing import Optional
from models.user_profile import UserProfile


def _clear():
    os.system("cls" if os.name == "nt" else "clear")


def _banner(title: str):
    width = 60
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def _section(title: str):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print("─" * 50)


def _prompt(label: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    value = input(f"  {label}{hint}: ").strip()
    return value if value else default


def _prompt_list(label: str) -> list:
    print(f"  {label} (comma-separated, press Enter when done):")
    raw = input("  > ").strip()
    return [s.strip() for s in raw.split(",") if s.strip()]


def _prompt_int(label: str, default: int = 0) -> int:
    while True:
        raw = _prompt(label, str(default))
        try:
            return int(raw)
        except ValueError:
            print("  ⚠  Please enter a whole number.")


def _prompt_bool(label: str) -> bool:
    raw = _prompt(f"{label} (y/n)", "n").lower()
    return raw in ("y", "yes")


class KioskInterface:
    """
    Step-by-step guided intake flow, displayed on the terminal.
    Returns a populated UserProfile.
    """

    def run_intake_flow(self) -> Optional[UserProfile]:
        """Walk the user through profile entry and return a UserProfile."""
        _clear()
        _banner("Smart Career Advisory Kiosk")
        print("\n  Welcome! This session takes about 5–10 minutes.")
        print("  Your data is encrypted and never shared without consent.\n")
        print("  Press CTRL+C at any time to exit.\n")
        input("  Press ENTER to begin → ")

        try:
            profile = UserProfile()
            self._step_personal(profile)
            self._step_education(profile)
            self._step_experience(profile)
            self._step_skills(profile)
            self._step_preferences(profile)
            self._confirm(profile)
            return profile

        except KeyboardInterrupt:
            print("\n\n  Session ended. Thank you for using the kiosk!")
            return None

    # ------------------------------------------------------------------
    # Intake steps
    # ------------------------------------------------------------------

    def _step_personal(self, profile: UserProfile):
        _clear()
        _section("Step 1 of 5 – Personal Information")
        profile.name     = _prompt("Full name")
        profile.age      = _prompt_int("Age", 25)
        profile.location = _prompt("City / State", "New York, NY")

    def _step_education(self, profile: UserProfile):
        _clear()
        _section("Step 2 of 5 – Education")
        levels = ["High School", "Associate's", "Bachelor's", "Master's", "PhD", "MBA", "Other"]
        print("  Education levels:")
        for i, lvl in enumerate(levels, 1):
            print(f"    {i}. {lvl}")
        choice = _prompt_int("Select number", 3)
        profile.education_level = levels[min(choice - 1, len(levels) - 1)]
        profile.field_of_study  = _prompt("Field of study", "Computer Science")

    def _step_experience(self, profile: UserProfile):
        _clear()
        _section("Step 3 of 5 – Work Experience")
        profile.years_of_experience = _prompt_int("Years of professional experience", 2)
        profile.previous_roles      = _prompt_list("Previous job titles")

    def _step_skills(self, profile: UserProfile):
        _clear()
        _section("Step 4 of 5 – Skills")
        print("  Tip: include programming languages, tools, frameworks…")
        profile.technical_skills = _prompt_list("Technical skills")
        profile.soft_skills      = _prompt_list("Soft skills (e.g., Leadership, Communication)")

    def _step_preferences(self, profile: UserProfile):
        _clear()
        _section("Step 5 of 5 – Career Preferences")
        profile.preferred_industry   = _prompt("Preferred industry", "Technology")
        work_types = ["Remote", "On-site", "Hybrid"]
        print("  Work type preference:")
        for i, wt in enumerate(work_types, 1):
            print(f"    {i}. {wt}")
        wt_choice = _prompt_int("Select number", 1)
        profile.preferred_work_type  = work_types[min(wt_choice - 1, 2)]
        profile.salary_expectation   = _prompt_int("Target annual salary (USD)", 80000)
        profile.relocation_willing   = _prompt_bool("Open to relocation?")

    def _confirm(self, profile: UserProfile):
        _clear()
        _section("Profile Summary – Please Confirm")
        d = profile.to_dict()
        for key, val in d.items():
            print(f"  {key.replace('_', ' ').title()}: {val}")
        print()
        ok = _prompt("Is this correct? (y/n)", "y").lower()
        if ok not in ("y", "yes"):
            print("\n  Please re-run the session to update your profile.")
            raise KeyboardInterrupt

    # ------------------------------------------------------------------
    # Output display
    # ------------------------------------------------------------------

    def display_report(self, report: dict):
        """Render the advisory report in the terminal."""
        _clear()
        _banner(f"Career Advisory Report – {report['user_name']}")

        # Career Matches
        _section("🎯 Top Career Recommendations")
        for i, career in enumerate(report["career_matches"], 1):
            print(f"\n  {i}. {career['title']}  ({career['match_score']} match)")
            print(f"     💰 Projected Salary : {career['projected_salary']}/yr")
            print(f"     📈 Job Growth       : {career['growth_label']}")
            if career["skill_gaps"]:
                print(f"     📚 Skills to Gain  : {', '.join(career['skill_gaps'][:3])}")

        # Job Matches
        _section("💼 Matching Open Positions (Live)")
        for i, job in enumerate(report["job_matches"], 1):
            print(f"\n  {i}. {job['title']} – {job['company']}")
            print(f"     📍 {job['location']}  |  {job['work_type']}  |  {job['salary']}")
            print(f"     🤝 Match Score : {job['match_score']}")
            print(f"     🔗 Apply       : {job['apply_url']}")

        # Salary Scenarios
        _section("💵 Salary Scenario Analysis")
        scenarios = report["salary_scenarios"]
        print(f"  Conservative : {scenarios['conservative']}")
        print(f"  Median       : {scenarios['median']}")
        print(f"  Optimistic   : {scenarios['optimistic']}")

        # Skill Gaps & Learning
        _section("📚 Skill Development Plan")
        if report["skill_gaps"]:
            print("  Priority skills to develop:")
            for gap in report["skill_gaps"][:5]:
                print(f"    • {gap}")
        paths = report["learning_paths"]
        if paths:
            top_career = next(iter(paths))
            print(f"\n  Recommended resources for {top_career}:")
            for resource in paths[top_career][:3]:
                print(f"    → {resource}")

        print("\n" + "=" * 60)
        print("  Session complete. Thank you for using the Smart Career Kiosk!")
        print("  A copy of this report has been saved securely.")
        print("=" * 60 + "\n")
