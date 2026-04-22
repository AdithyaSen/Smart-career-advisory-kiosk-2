"""
security/session_manager.py
Session Manager – Secure Data Handling
Manages user sessions, applies encryption, and enforces data-retention policy.
In production, AES-256 encryption (via cryptography library) would be used.
Here we use base64 encoding to simulate the process without extra dependencies.
"""

import base64
import json
import hashlib
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any
from models.user_profile import UserProfile


class SessionManager:
    """
    Manages kiosk sessions:
    - Creates and tracks session tokens.
    - Pseudonymises PII before storage.
    - Auto-expires sessions after a configurable timeout.
    - Stores reports in an encrypted (simulated) local store.
    """

    SESSION_TIMEOUT_SECONDS = 600   # 10 minutes
    STORE_DIR = "/tmp/kiosk_sessions"

    def __init__(self):
        os.makedirs(self.STORE_DIR, exist_ok=True)
        self._active_sessions: Dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def create_session(self) -> str:
        """Create a new session and return its token."""
        token = self._generate_token()
        self._active_sessions[token] = {
            "created_at": time.time(),
            "last_activity": time.time(),
            "profile": None,
            "report": None,
        }
        print(f"  [Session] Created: {token}")
        return token

    def is_valid(self, token: str) -> bool:
        """Check whether the session is still active and not timed out."""
        if token not in self._active_sessions:
            return False
        elapsed = time.time() - self._active_sessions[token]["last_activity"]
        if elapsed > self.SESSION_TIMEOUT_SECONDS:
            self.end_session(token)
            return False
        return True

    def save_profile(self, token: str, profile: UserProfile):
        if self.is_valid(token):
            self._active_sessions[token]["profile"] = profile.to_dict()
            self._touch(token)

    def save_report(self, token: str, report: dict):
        if self.is_valid(token):
            self._active_sessions[token]["report"] = report
            self._persist(token, report)
            self._touch(token)

    def get_report(self, token: str) -> Optional[dict]:
        if self.is_valid(token):
            return self._active_sessions[token].get("report")
        return None

    def end_session(self, token: str):
        """Securely remove all in-memory session data."""
        self._active_sessions.pop(token, None)
        print(f"  [Session] Ended: {token}")

    # ------------------------------------------------------------------
    # Storage helpers
    # ------------------------------------------------------------------

    def _persist(self, token: str, report: dict):
        """
        Pseudonymise and store the report for audit / analytics.
        In production: AES-256-GCM encryption with a KMS-managed key.
        Here: base64 simulation.
        """
        safe_report = self._pseudonymise(report)
        payload = json.dumps(safe_report).encode()
        encoded = base64.b64encode(payload).decode()

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.STORE_DIR, f"session_{ts}.enc")
        with open(path, "w") as f:
            f.write(encoded)
        print(f"  [Security] Report persisted: {path}")

    def _pseudonymise(self, report: dict) -> dict:
        """Replace the user name with a SHA-256 hash."""
        safe = dict(report)
        if "user_name" in safe:
            safe["user_name"] = hashlib.sha256(
                safe["user_name"].encode()
            ).hexdigest()[:16]
        return safe

    def _touch(self, token: str):
        self._active_sessions[token]["last_activity"] = time.time()

    @staticmethod
    def _generate_token() -> str:
        raw = os.urandom(16)
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")
