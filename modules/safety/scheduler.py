"""
Scheduler Module - Manages human-like session timing and breaks
Controls when the bot runs, how long it runs, and enforces rest periods
"""

from datetime import datetime, time, timedelta
import random
from typing import Tuple, Optional
from modules.helpers import print_lg, sleep
from .constants import SCHEDULER_CONFIG


class Scheduler:
    """
    Enterprise scheduler that enforces human-like working patterns.
    
    Features:
    - Active time windows (morning, afternoon, evening)
    - Random jitter (±22 min) on window boundaries
    - Micro-breaks after N applications
    - Weekend/vacation mode
    - Night-time run prevention
    """
    
    def __init__(self):
        self.config = SCHEDULER_CONFIG
        self.session_start_time = None
        self.applies_in_current_session = 0
        self.session_paused = False
        self.next_break_time = None
        
    def is_active_window(self) -> bool:
        """
        Check if current time is within active working windows.
        Returns True if bot should be running, False for rest periods.
        """
        if not self.config["enabled"]:
            return True
            
        current_time = datetime.now().time()
        
        # Prevent night runs (10 PM - 8 AM)
        if self.config["prevent_night_runs"]:
            if current_time >= time(22, 0) or current_time < time(8, 0):
                print_lg(f"[SCHEDULER] Night time detected ({current_time}). Bot sleeping until 8 AM.")
                return False
        
        # Check if today is a light day (weekend)
        today = datetime.now().weekday()  # 0=Monday, 6=Sunday
        if today in self.config["weekly_light_days"]:
            print_lg(f"[SCHEDULER] Weekend mode - will apply at 50% quota today")
        
        # Check against configured windows with jitter
        is_active = self._check_time_windows(current_time)
        return is_active
    
    def _check_time_windows(self, current_time: time) -> bool:
        """Check if current time falls within any active window (with jitter)"""
        windows = self.config["base_windows"]  # ["09:00-11:00", "13:00-15:00", "18:00-21:00"]
        jitter_range = self.config["window_jitter_minutes"]
        
        for window_str in windows:
            start_str, end_str = window_str.split("-")
            start_hour, start_min = map(int, start_str.split(":"))
            end_hour, end_min = map(int, end_str.split(":"))
            
            # Apply jitter to window boundaries
            jitter = random.randint(jitter_range[0], jitter_range[1])
            start_time = (datetime.combine(datetime.today(), time(start_hour, start_min)) 
                         + timedelta(minutes=jitter)).time()
            end_time = (datetime.combine(datetime.today(), time(end_hour, end_min)) 
                       + timedelta(minutes=jitter)).time()
            
            if start_time <= current_time <= end_time:
                return True
        
        return False
    
    def wait_until_active_window(self):
        """
        Block until next active window.
        Used if scheduler detects we're in a rest period.
        """
        wait_start = datetime.now()
        print_lg("[SCHEDULER] Not in active window. Waiting for next active window...")
        
        check_interval = 300  # Check every 5 minutes
        while not self.is_active_window():
            next_window = self._get_next_active_window()
            elapsed = (datetime.now() - wait_start).total_seconds() / 60
            print_lg(f"[SCHEDULER] Slept for {int(elapsed)} minutes. Next window at {next_window}")
            sleep(check_interval)
    
    def _get_next_active_window(self) -> str:
        """Calculate when the next active window starts"""
        now = datetime.now()
        windows = self.config["base_windows"]
        
        for window_str in windows:
            start_str, _ = window_str.split("-")
            start_hour, start_min = map(int, start_str.split(":"))
            window_start = datetime.combine(now.date(), time(start_hour, start_min))
            
            # Add jitter
            jitter = random.randint(*self.config["window_jitter_minutes"])
            window_start += timedelta(minutes=jitter)
            
            if window_start > now:
                return window_start.strftime("%H:%M")
        
        # If no window today, return first window tomorrow
        tomorrow = now + timedelta(days=1)
        first_window = self.config["base_windows"][0]
        start_str, _ = first_window.split("-")
        start_hour, start_min = map(int, start_str.split(":"))
        return f"Tomorrow {start_hour:02d}:{start_min:02d}"
    
    def start_session(self):
        """Call when starting a job application session"""
        self.session_start_time = datetime.now()
        self.applies_in_current_session = 0
        print_lg(f"[SCHEDULER] Session started at {self.session_start_time.strftime('%H:%M:%S')}")
    
    def record_application(self):
        """Call each time an application is submitted"""
        self.applies_in_current_session += 1
        
        # Check if micro-break is due
        micro_break_interval = self.config["micro_break_every_n_applies"]
        if self.applies_in_current_session % micro_break_interval == 0:
            self.take_micro_break()
    
    def take_micro_break(self):
        """Take a short 1-3 minute break to appear human"""
        break_duration = random.randint(60, 180)  # 60 to 180 seconds
        break_duration_str = f"{break_duration//60}m {break_duration%60}s" if break_duration > 60 else f"{break_duration}s"
        
        print_lg(f"[SCHEDULER] Taking micro-break for {break_duration_str} ({self.applies_in_current_session} apps so far)")
        sleep(break_duration)
        print_lg(f"[SCHEDULER] Micro-break complete. Resuming...")
    
    def calculate_adaptive_delay(self, base_delay: float, backoff_multiplier: float = 1.0) -> float:
        """
        Calculate delay between applications with randomness.
        Backoff multiplier increases if rate limiting is detected.
        
        Args:
            base_delay: Base delay in seconds (typically from RateLimiter)
            backoff_multiplier: Multiplier (e.g., 1.5x if we're being throttled)
        
        Returns:
            Actual delay in seconds
        """
        min_delay = self.config.get("min_delay_seconds", 120)
        max_delay = self.config.get("max_delay_seconds", 300)
        
        # Apply backoff
        min_delay *= backoff_multiplier
        max_delay *= backoff_multiplier
        
        # Cap at maximum
        max_backoff = self.config.get("max_backoff_delay_seconds", 900)
        max_delay = min(max_delay, max_backoff)
        
        # Random delay within range
        actual_delay = random.uniform(min_delay, max_delay)
        return actual_delay
    
    def end_session(self):
        """Call when ending a job application session"""
        if self.session_start_time:
            duration = (datetime.now() - self.session_start_time).total_seconds() / 60
            print_lg(f"[SCHEDULER] Session ended. Duration: {duration:.1f} minutes, Applications: {self.applies_in_current_session}")
    
    def should_stop_today(self) -> bool:
        """
        Determine if bot should stop for the rest of today.
        Called when daily quota is reached.
        """
        print_lg("[SCHEDULER] Daily quota reached. Bot will rest until tomorrow.")
        return True
    
    def get_session_info(self) -> dict:
        """Return current session statistics for logging"""
        return {
            "session_start": self.session_start_time,
            "applications_in_session": self.applies_in_current_session,
            "current_time": datetime.now(),
            "is_active_window": self.is_active_window(),
            "next_active_window": self._get_next_active_window() if not self.is_active_window() else "Now"
        }
