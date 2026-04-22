"""
kiosk_app.py
KioskApp – Main Orchestrator
Ties together the UI, AI engine, and security layers.
"""

from ui.kiosk_interface import KioskInterface
from ai_engine.recommendation_engine import RecommendationEngine
from security.session_manager import SessionManager


class KioskApp:
    """Top-level application controller for the Smart Career Advisory Kiosk."""

    def __init__(self):
        self.ui      = KioskInterface()
        self.engine  = RecommendationEngine()
        self.session = SessionManager()

    def run(self):
        """Main application loop."""
        # 1. Start a secure session
        token = self.session.create_session()

        # 2. Collect user profile via guided UI flow
        profile = self.ui.run_intake_flow()
        if profile is None:
            self.session.end_session(token)
            return

        # 3. Persist the profile
        self.session.save_profile(token, profile)

        # 4. Run the AI recommendation engine
        print("\n  ⏳ Analysing your profile with our AI engine…")
        report = self.engine.generate_report(profile)

        # 5. Persist the report
        self.session.save_report(token, report)

        # 6. Display results
        self.ui.display_report(report)

        # 7. Close session
        self.session.end_session(token)
