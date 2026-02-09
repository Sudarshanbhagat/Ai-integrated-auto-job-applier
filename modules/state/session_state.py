"""
Session State Manager - Persistent state across crashes and restarts
Allows automatic recovery from interruptions
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Any
from modules.helpers import print_lg


class SessionState:
    """
    Manages application session state (number of apps, current job, etc.)
    Persists to JSON file for crash recovery.
    """
    
    STATE_FILE = "logs/session_state.json"
    
    def __init__(self):
        self.state = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "applications_count": 0,
            "skipped_count": 0,
            "failed_count": 0,
            "last_application_time": None,
            "last_applied_job_id": None,
            "is_crashed": False,
            "crash_reason": None,
        }
        self.load_or_create()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def load_or_create(self):
        """Load existing state or create new one"""
        if os.path.exists(self.STATE_FILE):
            try:
                with open(self.STATE_FILE, 'r') as f:
                    saved_state = json.load(f)
                    self.state.update(saved_state)
                    print_lg(f"[STATE] Loaded session state from {self.SESSION_FILE}")
            except Exception as e:
                print_lg(f"[STATE] Warning: Failed to load session state: {e}")
                self._ensure_dir()
        else:
            self._ensure_dir()
    
    def _ensure_dir(self):
        """Ensure logs directory exists"""
        os.makedirs(os.path.dirname(self.STATE_FILE), exist_ok=True)
    
    def save(self):
        """Persist state to disk"""
        try:
            self._ensure_dir()
            with open(self.STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print_lg(f"[STATE] Warning: Failed to save session state: {e}")
    
    def record_application(self, job_id: str):
        """Record successful application"""
        self.state["applications_count"] += 1
        self.state["last_application_time"] = datetime.now().isoformat()
        self.state["last_applied_job_id"] = job_id
        self.save()
    
    def record_skip(self, reason: str = None):
        """Record skipped job"""
        self.state["skipped_count"] += 1
        self.save()
    
    def record_failure(self, error: str):
        """Record failed application"""
        self.state["failed_count"] += 1
        self.save()
    
    def mark_crashed(self, reason: str = None):
        """Mark session as crashed for recovery on restart"""
        self.state["is_crashed"] = True
        self.state["crash_reason"] = reason
        self.save()
        print_lg(f"[STATE] Session marked as crashed: {reason}")
    
    def mark_recovered(self):
        """Mark as recovered from crash"""
        self.state["is_crashed"] = False
        self.state["crash_reason"] = None
        self.save()
        print_lg("[STATE] Session recovered from crash")
    
    def get_stats(self) -> Dict:
        """Get current session statistics"""
        return {
            "session_id": self.state["session_id"],
            "duration_minutes": self._get_duration_minutes(),
            "applications": self.state["applications_count"],
            "skipped": self.state["skipped_count"],
            "failed": self.state["failed_count"],
            "last_applied_job": self.state["last_applied_job_id"],
            "is_crashed": self.state["is_crashed"],
        }
    
    def _get_duration_minutes(self) -> float:
        """Get elapsed time since session start"""
        start = datetime.fromisoformat(self.state["start_time"])
        elapsed = datetime.now() - start
        return elapsed.total_seconds() / 60
    
    def reset(self):
        """Reset state for new session"""
        self.state = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "applications_count": 0,
            "skipped_count": 0,
            "failed_count": 0,
            "last_application_time": None,
            "last_applied_job_id": None,
            "is_crashed": False,
            "crash_reason": None,
        }
        self.save()
        print_lg("[STATE] Session state reset")
