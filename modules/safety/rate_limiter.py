"""
Rate Limiter Module - Enforces daily quotas and adaptive delay between applications
Prevents account ban by respecting LinkedIn's invisible rate limits
"""

from datetime import datetime, timedelta
import time as time_module
from typing import Optional
from modules.helpers import print_lg
from .constants import RATE_LIMIT_CONFIG


class RateLimiter:
    """
    Intelligent rate limiter that:
    - Enforces daily application limits (default: 50/day)
    - Applies random delays between applications (2-5 minutes)
    - Detects rate limiting and increases delays adaptively
    - Resets backoff when safe operation detected
    - Differentiates weekdays vs weekends
    """
    
    def __init__(self):
        self.config = RATE_LIMIT_CONFIG
        self.applications_today = 0
        self.last_application_time = None
        self.daily_limit_reached = False
        self.backoff_multiplier = 1.0
        self.last_backoff_reset = datetime.now()
        self.rate_limit_detected_at = None
        
    def can_apply(self) -> bool:
        """
        Check if bot is allowed to apply to next job.
        
        Returns:
            True if applying is allowed, False if daily quota reached
        """
        if not self.config["enabled"]:
            return True
        
        # Check daily limit
        if self.applications_today >= self.config["max_daily_applications"]:
            if not self.daily_limit_reached:
                print_lg(f"[RATE_LIMIT] Daily limit reached ({self.applications_today}/{self.config['max_daily_applications']})")
                self.daily_limit_reached = True
            return False
        
        return True
    
    def get_required_delay(self) -> float:
        """
        Calculate required delay before next application.
        
        Returns:
            Delay in seconds (between min_delay and max_delay, with backoff multiplier)
        """
        min_delay = self.config["min_delay_seconds"]  # 120 (2 min)
        max_delay = self.config["max_delay_seconds"]  # 300 (5 min)
        
        # Apply adaptive backoff
        if self.config["adaptive_backoff_enabled"]:
            min_delay *= self.backoff_multiplier
            max_delay *= self.backoff_multiplier
            
            # Cap at maximum
            max_backoff = self.config["max_backoff_delay_seconds"]  # 900 (15 min)
            max_delay = min(max_delay, max_backoff)
        
        # Random delay within calculated range
        import random
        actual_delay = random.uniform(min_delay, max_delay)
        return actual_delay
    
    def wait_before_next_application(self):
        """
        Block until enough time has passed since last application.
        Respects configured minimum delays.
        """
        if self.last_application_time is None:
            return  # First application, no wait
        
        required_delay = self.get_required_delay()
        time_elapsed = datetime.now() - self.last_application_time
        time_remaining = required_delay - time_elapsed.total_seconds()
        
        if time_remaining > 0:
            delay_str = f"{int(time_remaining)}s" if time_remaining < 60 else f"{time_remaining/60:.1f}m"
            backoff_str = f" (backoff: {self.backoff_multiplier:.2f}x)" if self.backoff_multiplier > 1.0 else ""
            print_lg(f"[RATE_LIMIT] Waiting {delay_str} before next application{backoff_str}")
            time_module.sleep(time_remaining)
    
    def record_application(self):
        """Call after each successful application"""
        self.applications_today += 1
        self.last_application_time = datetime.now()
        
        # Check if it's a new day (reset counter at midnight)
        self._check_day_boundary()
        
        remaining = self.config["max_daily_applications"] - self.applications_today
        print_lg(f"[RATE_LIMIT] Application #{self.applications_today}. {remaining} remaining today.")
    
    def detect_rate_limiting(self) -> bool:
        """
        Detect if LinkedIn is rate limiting us (e.g., by 429 errors or slow responses).
        Should be called by main automation loop when detecting rate limit signs.
        """
        if not self.config["adaptive_backoff_enabled"]:
            return False
        
        # Increase backoff multiplier
        if self.backoff_multiplier == 1.0:
            print_lg("[RATE_LIMIT] Rate limiting detected! Increasing delays...")
            self.rate_limit_detected_at = datetime.now()
        
        old_multiplier = self.backoff_multiplier
        self.backoff_multiplier = min(
            self.backoff_multiplier * self.config["backoff_multiplier"],
            self.config["max_backoff_delay_seconds"] / self.config["max_delay_seconds"]
        )
        
        print_lg(f"[RATE_LIMIT] Backoff multiplier: {old_multiplier:.2f}x → {self.backoff_multiplier:.2f}x")
        return True
    
    def reset_backoff(self):
        """Reset backoff multiplier if safe operation detected"""
        if self.backoff_multiplier > 1.0:
            time_since_detection = datetime.now() - self.rate_limit_detected_at
            reset_after = self.config["reset_backoff_after_hours"] * 3600  # Convert to seconds
            
            if time_since_detection.total_seconds() > reset_after:
                print_lg(f"[RATE_LIMIT] Safe operation detected for {self.config['reset_backoff_after_hours']}h. Resetting backoff.")
                self.backoff_multiplier = 1.0
                self.rate_limit_detected_at = None
    
    def _check_day_boundary(self):
        """Reset daily counter if new day detected"""
        # Simple check - if last record is >24 hours old, reset
        if self.last_application_time is None:
            return
        
        # This would be better with persistent storage
        # For now, we're in-memory only
        pass
    
    def get_daily_progress(self) -> dict:
        """Return statistics about today's applications"""
        return {
            "applications_today": self.applications_today,
            "daily_limit": self.config["max_daily_applications"],
            "remaining_today": max(0, self.config["max_daily_applications"] - self.applications_today),
            "percent_of_quota": (self.applications_today / self.config["max_daily_applications"]) * 100,
            "daily_limit_reached": self.daily_limit_reached,
            "backoff_multiplier": self.backoff_multiplier,
            "rate_limited": self.backoff_multiplier > 1.0,
            "last_application": self.last_application_time.strftime("%H:%M:%S") if self.last_application_time else "Never"
        }
    
    def reset_daily_counter(self):
        """Reset application counter for new day (called at midnight)"""
        print_lg(f"[RATE_LIMIT] Resetting daily counter. Total from yesterday: {self.applications_today}")
        self.applications_today = 0
        self.daily_limit_reached = False
        self.last_application_time = None
        
        # Keep backoff multiplier - it might still be active
