# Smart Career Advisory Kiosk

AI-driven system for personalized career guidance using real-time labor market analytics.

## Project Structure

```
smart_career_kiosk/
├── main.py                          # Entry point
├── kiosk_app.py                     # Main orchestrator
├── requirements.txt
├── models/
│   ├── user_profile.py              # UserProfile data model
│   └── job_listing.py               # JobListing data model
├── ai_engine/
│   ├── career_mapping_nn.py         # Career Mapping Neural Network (CMNN)
│   ├── nlp_job_parser.py            # NLP Job Parsing Engine
│   └── recommendation_engine.py    # Report generation orchestrator
├── ui/
│   └── kiosk_interface.py          # CLI/touchscreen interface simulation
├── security/
│   └── session_manager.py          # Session & data security layer
└── tests/
    └── test_ai_engine.py           # Unit tests
```

## Setup & Run

```bash
# No external dependencies required for the core demo
python main.py

# Run unit tests
python -m pytest tests/ -v

# Optional: install production ML libraries
pip install -r requirements.txt
```

## Key Components

| Component | Description |
|-----------|-------------|
| **CMNN** | Career Mapping Neural Network – scores career path fit |
| **NLP Job Parser** | Extracts skills & matches live job postings |
| **Recommendation Engine** | Combines CMNN + NLP into a unified report |
| **Kiosk Interface** | Step-by-step guided intake (touchscreen simulation) |
| **Session Manager** | Secure session lifecycle + pseudonymised storage |

## Architecture

```
User → Kiosk Interface → KioskApp
                              ↓
                   RecommendationEngine
                    ↙              ↘
            CareerMappingNN    NLPJobParser
                    ↘              ↙
                  Advisory Report
                              ↓
                    SessionManager (secure store)
```
