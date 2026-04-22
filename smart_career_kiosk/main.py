"""
Smart Career Advisory Kiosk - Main Application Entry Point
AI-driven system for personalized career guidance using real-time labor market analytics.
"""

import sys
from kiosk_app import KioskApp

def main():
    print("=" * 60)
    print("  Smart Career Advisory Kiosk")
    print("  AI-Powered Career Guidance System")
    print("=" * 60)
    app = KioskApp()
    app.run()

if __name__ == "__main__":
    main()
