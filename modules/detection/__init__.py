"""
Detection Module - Identifies platforms, challenges, and problematic conditions
Auto-skips jobs that would cause issues or require manual intervention
"""

import re
from typing import Optional, List, Tuple
from modules.helpers import print_lg
from .constants import SKIP_CONFIG, CHALLENGE_PATTERNS


class SkipEngine:
    """
    Intelligently detects and skips problematic jobs:
    - External platforms (Workday, iCIMS, etc.)
    - Challenge conditions (CAPTCHA, OTP, assessment)
    - Spam/reposted jobs
    - Already applied jobs
    """
    
    def __init__(self):
        self.config = SKIP_CONFIG
        self.skipped_jobs = []
        self.skip_reasons_counters = {}
    
    def should_skip_platform(self, job_url: str, job_description: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if job is on external platform that we can't handle.
        
        Args:
            job_url: LinkedIn job posting URL
            job_description: Job description text
            
        Returns:
            Tuple of (should_skip, reason)
        """
        skip_platforms = self.config.get("skip_platforms", [])
        description_lower = job_description.lower()
        
        for platform in skip_platforms:
            # Check in URL
            if platform.lower() in job_url.lower():
                reason = f"Platform detected: {platform}"
                self._log_skip(reason)
                return True, reason
            
            # Check in description
            patterns = {
                "workday": ["apply on workday", "workday", "myworkdayjobs"],
                "greenhouse": ["powered by greenhouse", "greenhouse"],
                "icims": ["icims"],
                "lever": ["lever"],
                "successfactors": ["successfactors"],
            }
            
            for key, keywords in patterns.items():
                if platform.lower() in key.lower():
                    for keyword in keywords:
                        if keyword in description_lower:
                            reason = f"External platform detected: {key}"
                            self._log_skip(reason)
                            return True, reason
        
        return False, None
    
    def should_skip_due_to_challenge(self, page_source: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if page contains challenges we can't handle.
        
        Args:
            page_source: Full HTML page source
            
        Returns:
            Tuple of (should_skip, challenge_type)
        """
        page_lower = page_source.lower()
        skip_conditions = self.config.get("skip_conditions", [])
        
        for condition in skip_conditions:
            # Get patterns for this condition
            patterns = CHALLENGE_PATTERNS.get(condition, [])
            
            for pattern in patterns:
                if pattern.lower() in page_lower:
                    reason = f"Challenge detected: {condition}"
                    self._log_skip(reason)
                    return True, condition
        
        return False, None
    
    def should_skip_due_to_relevance(self, job_data: dict) -> Tuple[bool, Optional[str]]:
        """
        Determine if job should be skipped due to relevance rules.
        
        Args:
            job_data: Dictionary containing job info (title, company, date_posted, etc.)
            
        Returns:
            Tuple of (should_skip, reason)
        """
        # Check if already applied
        if job_data.get("already_applied", False):
            reason = "Already applied to this job"
            self._log_skip(reason)
            return True, reason
        
        # Check for spam indicators
        title_lower = job_data.get("title", "").lower()
        company_lower = job_data.get("company", "").lower()
        
        spam_keywords = [
            "promote",
            "make money",
            "work from home",
            "flexible hours",
            "no experience needed",
        ]
        
        for keyword in spam_keywords:
            if keyword in title_lower or keyword in company_lower:
                reason = f"Spam indicator detected: '{keyword}'"
                self._log_skip(reason)
                return True, reason
        
        # Check job age (skip if too old)
        min_post_age = self.config.get("relevance_filter", {}).get("minimum_post_age_hours", 2)
        if job_data.get("days_posted", 999) > (min_post_age / 24):
            reason = f"Job too old ({job_data.get('days_posted', 0):.1f} days)"
            self._log_skip(reason)
            return True, reason
        
        # Check for reposted jobs
        if job_data.get("is_reposted", False):
            avoid_reposted = self.config.get("relevance_filter", {}).get("avoid_reposted_jobs", True)
            if avoid_reposted:
                reason = "Job appears to be reposted"
                self._log_skip(reason)
                return True, reason
        
        return False, None
    
    def detect_assessment_requirement(self, page_source: str) -> bool:
        """
        Check if the Easy Apply form includes an assessment/skills test.
        """
        patterns = CHALLENGE_PATTERNS.get("assessment", [])
        page_lower = page_source.lower()
        
        for pattern in patterns:
            if pattern.lower() in page_lower:
                print_lg("[SKIP] Assessment detected - auto-skipping")
                return True
        
        return False
    
    def detect_video_interview_requirement(self, page_source: str) -> bool:
        """
        Check if a one-way video interview is required in the application.
        """
        patterns = CHALLENGE_PATTERNS.get("video_interview", [])
        page_lower = page_source.lower()
        
        for pattern in patterns:
            if pattern.lower() in page_lower:
                print_lg("[SKIP] Video interview requirement detected - auto-skipping")
                return True
        
        return False
    
    def detect_phone_verification_requirement(self, page_source: str) -> bool:
        """
        Check if phone verification is required before applying.
        """
        patterns = CHALLENGE_PATTERNS.get("phone_verification", [])
        page_lower = page_source.lower()
        
        for pattern in patterns:
            if pattern.lower() in page_lower:
                print_lg("[SKIP] Phone verification required - auto-skipping")
                return True
        
        return False
    
    def detect_captcha(self, page_source: str) -> bool:
        """
        Detect CAPTCHA challenge on page.
        """
        captcha_indicators = [
            "recaptcha",
            "h-captcha",
            "check your browser",
            "i'm not a robot",
            "verify that you're human",
        ]
        
        page_lower = page_source.lower()
        for indicator in captcha_indicators:
            if indicator in page_lower:
                print_lg("[SKIP] CAPTCHA detected - auto-skipping")
                return True
        
        return False
    
    def _log_skip(self, reason: str):
        """Log a skip reason for analytics"""
        self.skipped_jobs.append({
            "timestamp": __import__('datetime').datetime.now(),
            "reason": reason
        })
        
        # Update counter
        self.skip_reasons_counters[reason] = self.skip_reasons_counters.get(reason, 0) + 1
        print_lg(f"[SKIP] {reason}")
    
    def get_skip_stats(self) -> dict:
        """Return statistics about skipped jobs"""
        return {
            "total_skipped": len(self.skipped_jobs),
            "skip_reasons": self.skip_reasons_counters,
            "most_common_reason": max(self.skip_reasons_counters.items(), key=lambda x: x[1])[0] 
                if self.skip_reasons_counters else None
        }
