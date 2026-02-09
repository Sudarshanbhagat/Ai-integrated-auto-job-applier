"""
Safety & Scheduling Constants
These values control bot behavior timing and rate limiting
"""

from enum import Enum
from datetime import time

class TimeWindow(Enum):
    """Active hours for the bot - when it should be running"""
    MORNING = (time(9, 0), time(11, 0))      # 9 AM - 11 AM
    AFTERNOON = (time(13, 0), time(15, 0))   # 1 PM - 3 PM
    EVENING = (time(18, 0), time(21, 0))     # 6 PM - 9 PM

# Scheduler Configuration
SCHEDULER_CONFIG = {
    "enabled": True,
    "base_windows": ["09:00-11:00", "13:00-15:00", "18:00-21:00"],
    "window_jitter_minutes": (-22, 22),           # ±22 minutes variance
    "prevent_night_runs": True,                    # Don't apply 10 PM - 8 AM
    "micro_break_every_n_applies": 5,              # 1-3 minute break after every 5 apps
    "weekly_light_days": [5, 6],                   # Saturday (5), Sunday (6) - 50% quota
    "vacation_mode": False,                        # Completely disable if True
}

# Rate Limiting Configuration
RATE_LIMIT_CONFIG = {
    "enabled": True,
    "max_daily_applications": 50,                  # LinkedIn's soft limit is ~75/day
    "min_delay_seconds": 120,                      # 2 minutes minimum between apps
    "max_delay_seconds": 300,                      # 5 minutes maximum between apps
    "adaptive_backoff_enabled": True,              # Increase delays if detecting rate limiting
    "backoff_multiplier": 1.5,                     # Multiply delay by this if rate limited
    "max_backoff_delay_seconds": 900,              # Never exceed 15 minutes
    "reset_backoff_after_hours": 1,                # Reset backoff multiplier after 1 hour of safe operation
}

# Behavioral Heuristics
BEHAVIOR_CONFIG = {
    "human_mouse_movement": True,                  # Simulate realistic mouse movements
    "variable_scroll_speed": True,                 # Random scroll velocities
    "pre_apply_research": True,                    # Read job desc before applying
    "random_interruption_probability": 0.08,       # 8% chance to pause randomly
    "random_pause_duration_sec": (30, 180),        # 30 sec to 3 min random pauses
    "save_jobs_probability": 0.15,                 # 15% chance to save job instead of apply
    "skip_good_job_probability": 0.05,             # 5% chance to skip even if suitable
    "typo_probability": 0.02,                      # 2% chance to make small typos in open text
    "slow_typing_enabled": True,                   # Type at human speed, not instant
    "typing_speed_wpm": (40, 80),                  # Words per minute (40-80)
}

# Stealth Engine Configuration
STEALTH_CONFIG = {
    "hide_navigator_webdriver": True,              # Remove navigator.webdriver flag
    "cdc_string_removal": True,                    # Remove Chrome DevTools Protocol markers
    "js_fingerprint_patch": True,                  # Patch JS fingerprinting detection
    "headless_mode": False,                        # Avoid headless - too obvious
    "disable_blink_features": [                    # Disable automation-related features
        "AutomationControlled",
        "EnableAutomation"
    ],
    "user_agent_rotation": True,                   # Rotate UA on each session
    "canvas_noise": True,                          # Add noise to canvas fingerprinting
    "timezone_matching": True,                     # Match system timezone
    "language_matching": True,                     # Match system language
    "screen_resolution_variation": True,           # Vary screen resolution
}

# Platform Skip Configuration
SKIP_CONFIG = {
    "skip_platforms": [
        "workday",
        "myworkdayjobs",
        "successfactors",
        "oraclecloud",
        "icims",
        "greenhouse",
        "lever",
        "ashby"
    ],
    "skip_conditions": [
        "captcha",
        "otp",
        "phone_verification",
        "email_verification",
        "assessment",
        "video_interview",
        "security_challenge"
    ],
    "auto_recover_from_skip": True,                # Try next job after skip
    "log_skips_to_database": True,                 # Track skipped reasons for analytics
}

# Challenge Detection Patterns
CHALLENGE_PATTERNS = {
    "captcha": [
        "check your browser",
        "recaptcha",
        "i'm not a robot",
        "verify that you're human"
    ],
    "otp": [
        "enter the code",
        "6-digit code",
        "code sent to",
        "verification code"
    ],
    "phone_verification": [
        "verify with your phone",
        "phone number",
        "send code to phone"
    ],
    "assessment": [
        "assessment",
        "take test",
        "coding challenge",
        "skills test"
    ],
    "video_interview": [
        "video interview",
        "record yourself",
        "one-way video"
    ]
}

# Resume Configuration
RESUME_CONFIG = {
    "enabled": True,
    "resume_types": {
        "software": "all resumes/software.pdf",
        "backend": "all resumes/backend.pdf",
        "frontend": "all resumes/frontend.pdf",
        "fullstack": "all resumes/fullstack.pdf",
        "embedded": "all resumes/embedded.pdf",
        "cybersecurity": "all resumes/cybersecurity.pdf"
    },
    "skill_extraction_enabled": True,
    "auto_mapping_enabled": True,
    "llm_fallback_enabled": True,
    "generate_variants": True,                     # Create 3-5 formatting variants
    "ats_friendly_templates": True,                # Use ATS-safe formatting
}

# Logging & Observability
LOGGING_CONFIG = {
    "log_level": "INFO",
    "sanitize_sensitive_data": True,               # Remove passwords, API keys from logs
    "log_skips": True,
    "log_challenges": True,
    "screenshot_on_error": True,
    "auto_cleanup_old_logs": True,                 # Delete logs older than 30 days
}

# Health Check Configuration
HEALTH_CHECK_CONFIG = {
    "check_interval_seconds": 300,                 # Every 5 minutes
    "validate_session_alive": True,
    "validate_api_connectivity": True,
    "validate_browser_responsive": True,
}

# Session Persistence
SESSION_CONFIG = {
    "persistence_enabled": True,
    "auto_resume_on_crash": True,
    "max_retries_on_error": 3,
    "retry_delay_seconds": 30,
    "database_path": "logs/session_state.db",
}
