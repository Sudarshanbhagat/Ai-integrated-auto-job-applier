"""
Account Monitor - Real-time account security monitoring and anomaly detection
Monitors login patterns, application rates, and suspicious activities
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque
from modules.helpers import print_lg


class AccountMonitor:
    """
    Real-time account monitoring and anomaly detection.
    
    Features:
    - Track login patterns (success/failure, IP, location)
    - Monitor application rates (alert on burst activity)
    - Detect unusual activities (timing, location changes)
    - Health scoring (0-100 scale)
    - Anomaly pattern detection
    """
    
    def __init__(self):
        """Initialize account monitor."""
        # Activity tracking (time-series data)
        self.login_history = deque(maxlen=1000)        # Last 1000 logins
        self.application_history = deque(maxlen=5000)  # Last 5000 applications
        self.error_history = deque(maxlen=500)         # Last 500 errors
        
        # Statistics
        self.health_score = 100
        self.last_health_check = datetime.now()
        self.startup_time = datetime.now()
        
        # Thresholds (configurable)
        self.max_applications_per_hour = 20
        self.max_failed_logins_per_day = 3
        self.max_errors_per_hour = 5
        self.unusual_login_location_timeout_hours = 24
        
        print_lg("[MONITOR] Initialized Account Monitor")
    
    def record_login(self, username: str, success: bool, ip_address: str = None,
                    location: str = None) -> bool:
        """
        Record a login attempt.
        
        Args:
            username: Username
            success: Whether login was successful
            ip_address: IP address used for login
            location: Geographic location of login
        
        Returns:
            True if recorded successfully
        """
        try:
            login_event = {
                "timestamp": datetime.now().isoformat(),
                "username": username,
                "success": success,
                "ip_address": ip_address,
                "location": location
            }
            
            self.login_history.append(login_event)
            
            # Update health score for failed logins
            if not success:
                failed_count = self._count_failed_logins_today()
                if failed_count > self.max_failed_logins_per_day:
                    self.health_score = max(0, self.health_score - 10)
            
            print_lg(f"[MONITOR] Login recorded: {username} ({'success' if success else 'failed'})")
            return True
            
        except Exception as e:
            print_lg(f"[MONITOR] Error recording login: {e}")
            return False
    
    def record_application(self, company: str, job_title: str, success: bool = True) -> bool:
        """
        Record a job application.
        
        Args:
            company: Company name
            job_title: Job title
            success: Whether application submitted successfully
        
        Returns:
            True if recorded successfully
        """
        try:
            app_event = {
                "timestamp": datetime.now().isoformat(),
                "company": company,
                "job_title": job_title,
                "success": success
            }
            
            self.application_history.append(app_event)
            
            print_lg(f"[MONITOR] Application recorded: {company} - {job_title}")
            return True
            
        except Exception as e:
            print_lg(f"[MONITOR] Error recording application: {e}")
            return False
    
    def record_error(self, error_type: str, error_message: str, context: Dict = None) -> bool:
        """
        Record an error event.
        
        Args:
            error_type: Type of error (http_error, timeout, auth_error, etc.)
            error_message: Error message
            context: Additional context about the error
        
        Returns:
            True if recorded successfully
        """
        try:
            error_event = {
                "timestamp": datetime.now().isoformat(),
                "error_type": error_type,
                "message": error_message,
                "context": context or {}
            }
            
            self.error_history.append(error_event)
            
            # Update health score for errors
            error_count = self._count_errors_last_hour()
            if error_count > self.max_errors_per_hour:
                self.health_score = max(0, self.health_score - 5)
            
            print_lg(f"[MONITOR] Error recorded: {error_type}")
            return True
            
        except Exception as e:
            print_lg(f"[MONITOR] Error recording error: {e}")
            return False
    
    def detect_suspicious_patterns(self) -> List[Dict]:
        """
        Detect suspicious activity patterns.
        
        Returns:
            List of suspicious patterns detected
        """
        suspicious_list = []
        
        try:
            # Pattern 1: Burst application activity (>max per hour)
            apps_per_hour = self._count_applications_last_hour()
            if apps_per_hour > self.max_applications_per_hour:
                suspicious_list.append({
                    "pattern": "burst_activity",
                    "severity": "critical",
                    "description": f"{apps_per_hour} applications in last hour (threshold: {self.max_applications_per_hour})",
                    "timestamp": datetime.now().isoformat()
                })
                self.health_score = max(0, self.health_score - 15)
            
            # Pattern 2: Multiple failed login attempts
            failed_logins = self._count_failed_logins_today()
            if failed_logins > self.max_failed_logins_per_day:
                suspicious_list.append({
                    "pattern": "failed_logins",
                    "severity": "high",
                    "description": f"{failed_logins} failed logins today (threshold: {self.max_failed_logins_per_day})",
                    "timestamp": datetime.now().isoformat()
                })
                self.health_score = max(0, self.health_score - 10)
            
            # Pattern 3: High error rate
            errors_per_hour = self._count_errors_last_hour()
            if errors_per_hour > self.max_errors_per_hour:
                suspicious_list.append({
                    "pattern": "error_spike",
                    "severity": "high",
                    "description": f"{errors_per_hour} errors in last hour (threshold: {self.max_errors_per_hour})",
                    "timestamp": datetime.now().isoformat()
                })
                self.health_score = max(0, self.health_score - 10)
            
            # Pattern 4: Login from unusual location
            unusual_locations = self._detect_unusual_locations()
            if unusual_locations:
                suspicious_list.append({
                    "pattern": "unusual_location",
                    "severity": "medium",
                    "description": f"Login from new location(s): {', '.join(unusual_locations)}",
                    "timestamp": datetime.now().isoformat()
                })
                self.health_score = max(0, self.health_score - 5)
            
            # Pattern 5: Unusual login times (late night/early morning)
            unusual_times = self._detect_unusual_times()
            if unusual_times:
                suspicious_list.append({
                    "pattern": "unusual_time",
                    "severity": "low",
                    "description": f"Login at unusual times: {unusual_times}",
                    "timestamp": datetime.now().isoformat()
                })
                self.health_score = max(0, self.health_score - 3)
            
            # Log critical patterns
            for pattern in suspicious_list:
                if pattern['severity'] in ['critical', 'high']:
                    print_lg(f"[MONITOR] 🚨 {pattern['severity'].upper()}: {pattern['pattern']} - {pattern['description']}")
            
            return suspicious_list
            
        except Exception as e:
            print_lg(f"[MONITOR] Error detecting patterns: {e}")
            return []
    
    def get_health_status(self) -> Dict:
        """
        Get overall account health status.
        
        Returns:
            Dict with health status and metrics
        """
        try:
            now = datetime.now()
            uptime = (now - self.startup_time).total_seconds()
            
            # Normalize health score to 0-100
            health_score = max(0, min(100, self.health_score))
            
            # Determine status based on score
            if health_score >= 80:
                status = "HEALTHY"
            elif health_score >= 50:
                status = "WARNING"
            else:
                status = "CRITICAL"
            
            return {
                "timestamp": now.isoformat(),
                "health_score": health_score,
                "status": status,
                "uptime_seconds": int(uptime),
                "metrics": {
                    "total_logins": len(self.login_history),
                    "total_applications": len(self.application_history),
                    "total_errors": len(self.error_history),
                    "logins_today": self._count_logins_today(),
                    "logins_failed_today": self._count_failed_logins_today(),
                    "applications_last_hour": self._count_applications_last_hour(),
                    "errors_last_hour": self._count_errors_last_hour()
                },
                "last_update": self.last_health_check.isoformat()
            }
            
        except Exception as e:
            print_lg(f"[MONITOR] Error getting health status: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def get_activity_summary(self, hours: int = 24) -> Dict:
        """
        Get activity summary for the last N hours.
        
        Args:
            hours: Number of hours to summarize
        
        Returns:
            Dict with activity summary
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter recent activities
            recent_logins = [e for e in self.login_history 
                           if datetime.fromisoformat(e['timestamp']) >= cutoff_time]
            recent_apps = [e for e in self.application_history 
                          if datetime.fromisoformat(e['timestamp']) >= cutoff_time]
            recent_errors = [e for e in self.error_history 
                            if datetime.fromisoformat(e['timestamp']) >= cutoff_time]
            
            # Calculate statistics
            successful_apps = sum(1 for a in recent_apps if a.get('success', True))
            failed_apps = len(recent_apps) - successful_apps
            successful_logins = sum(1 for l in recent_logins if l['success'])
            failed_logins = len(recent_logins) - successful_logins
            
            # Group errors by type
            errors_by_type = {}
            for error in recent_errors:
                error_type = error['error_type']
                errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
            
            return {
                "time_period_hours": hours,
                "logins": {
                    "total": len(recent_logins),
                    "successful": successful_logins,
                    "failed": failed_logins
                },
                "applications": {
                    "total": len(recent_apps),
                    "successful": successful_apps,
                    "failed": failed_apps
                },
                "errors": {
                    "total": len(recent_errors),
                    "by_type": errors_by_type
                }
            }
            
        except Exception as e:
            print_lg(f"[MONITOR] Error getting activity summary: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    def _count_logins_today(self) -> int:
        """Count total logins in the last 24 hours."""
        cutoff = datetime.now() - timedelta(hours=24)
        return sum(1 for e in self.login_history 
                  if datetime.fromisoformat(e['timestamp']) >= cutoff)
    
    def _count_failed_logins_today(self) -> int:
        """Count failed logins in the last 24 hours."""
        cutoff = datetime.now() - timedelta(hours=24)
        return sum(1 for e in self.login_history 
                  if not e['success'] and datetime.fromisoformat(e['timestamp']) >= cutoff)
    
    def _count_applications_last_hour(self) -> int:
        """Count applications in the last hour."""
        cutoff = datetime.now() - timedelta(hours=1)
        return sum(1 for e in self.application_history 
                  if datetime.fromisoformat(e['timestamp']) >= cutoff)
    
    def _count_errors_last_hour(self) -> int:
        """Count errors in the last hour."""
        cutoff = datetime.now() - timedelta(hours=1)
        return sum(1 for e in self.error_history 
                  if datetime.fromisoformat(e['timestamp']) >= cutoff)
    
    def _detect_unusual_locations(self) -> List[str]:
        """Detect logins from unusual locations."""
        unusual = []
        
        if len(self.login_history) < 2:
            return unusual
        
        recent_logins = list(self.login_history)[-10:]  # Last 10 logins
        locations = [e.get('location') for e in recent_logins 
                    if e.get('location') and e['success']]
        
        if locations:
            current_location = locations[-1]
            previous_locations = locations[:-1]
            
            # If current location differs from all previous ones in the period
            if current_location not in previous_locations and current_location:
                unusual.append(current_location)
        
        return unusual
    
    def _detect_unusual_times(self) -> str:
        """Detect logins at unusual times (0-5 AM)."""
        unusual_count = 0
        
        cutoff = datetime.now() - timedelta(hours=24)
        recent_logins = [e for e in self.login_history 
                        if datetime.fromisoformat(e['timestamp']) >= cutoff and e['success']]
        
        for login in recent_logins:
            login_time = datetime.fromisoformat(login['timestamp'])
            hour = login_time.hour
            
            # Unusual hours: midnight to 5 AM
            if 0 <= hour < 5:
                unusual_count += 1
        
        if unusual_count > 0:
            return f"{unusual_count} logins between 12 AM - 5 AM"
        
        return ""
    
    def reset_health_score(self) -> bool:
        """Reset health score to 100."""
        try:
            self.health_score = 100
            self.last_health_check = datetime.now()
            print_lg("[MONITOR] Health score reset to 100")
            return True
        except Exception as e:
            print_lg(f"[MONITOR] Error resetting health score: {e}")
            return False
    
    def export_monitoring_data(self, filepath: str) -> bool:
        """
        Export all monitoring data to JSON file.
        
        Args:
            filepath: Path to save monitoring data
        
        Returns:
            True if exported successfully
        """
        try:
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "health_status": self.get_health_status(),
                "activity_summary": self.get_activity_summary(24),
                "login_history": list(self.login_history),
                "application_history": list(self.application_history),
                "error_history": list(self.error_history)
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            print_lg(f"[MONITOR] Exported monitoring data to {filepath}")
            return True
            
        except Exception as e:
            print_lg(f"[MONITOR] Error exporting monitoring data: {e}")
            return False
    
    def health_check(self) -> Dict:
        """
        Check monitor health.
        
        Returns:
            Dict with monitor status
        """
        try:
            return {
                "status": "healthy",
                "initialized": True,
                "startup_time": self.startup_time.isoformat(),
                "uptime_seconds": int((datetime.now() - self.startup_time).total_seconds()),
                "histories": {
                    "logins": len(self.login_history),
                    "applications": len(self.application_history),
                    "errors": len(self.error_history)
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_stats(self) -> Dict:
        """Get audit statistics."""
        total_logins = len(self.login_history)
        successful_logins = sum(1 for e in self.login_history if e['success'])
        failed_logins = total_logins - successful_logins
        
        return {
            "total_logins": total_logins,
            "successful_logins": successful_logins,
            "failed_logins": failed_logins,
            "total_applications": len(self.application_history),
            "total_errors": len(self.error_history),
            "health_score": self.health_score
        }
