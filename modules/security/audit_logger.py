"""
Audit Logger - Security event logging and tracking
Logs all security-relevant events for monitoring and compliance
"""

import json
import os
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from modules.helpers import print_lg


class AuditLogger:
    """
    Audit trail for security events.
    
    Features:
    - Log security events (logins, credential access, changes)
    - Filter logs by event type, date, severity, user
    - Export logs in JSON/CSV formats
    - Real-time alerts for high-severity events
    - Automatic log rotation and retention
    """
    
    # Event types
    EVENT_TYPES = {
        "login": "User login attempt",
        "logout": "User logout",
        "credential_access": "Credential accessed from vault",
        "credential_modify": "Credential modified",
        "credential_rotate": "Credential rotated",
        "api_call": "API call made",
        "error": "Error occurred",
        "suspicious_activity": "Suspicious activity detected",
        "account_change": "Account settings changed",
        "policy_violation": "Security policy violated"
    }
    
    # Severity levels
    SEVERITY_LEVELS = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }
    
    def __init__(self, log_dir: str = "logs/security"):
        """
        Initialize audit logger.
        
        Args:
            log_dir: Directory to store audit logs
        """
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "audit.log")
        self.events_in_memory = []
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        print_lg("[AUDIT] Initialized Audit Logger")
        
        print_lg("[AUDIT] Initialized Audit Logger")
    
    def log_event(self, event_type: str, details: Dict = None, 
                  username: str = "system", severity: str = "low") -> bool:
        """
        Log a security event.
        
        Args:
            event_type: Type of event (must be in EVENT_TYPES)
            details: Additional event details
            username: Username associated with event
            severity: Event severity (low/medium/high/critical)
        
        Returns:
            True if logged successfully
        """
        try:
            if event_type not in self.EVENT_TYPES:
                print_lg(f"[AUDIT] Unknown event type: {event_type}")
                return False
            
            if severity not in self.SEVERITY_LEVELS:
                severity = "low"
            
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "severity": severity,
                "username": username,
                "description": self.EVENT_TYPES[event_type],
                "details": details or {}
            }
            
            # Add to in-memory list
            self.events_in_memory.append(event)
            
            # Write to log file
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
            
            # Alert on critical events
            if severity == "critical":
                print_lg(f"[AUDIT] ⚠️ CRITICAL: {event_type} - {details}")
            
            return True
            
        except Exception as e:
            print_lg(f"[AUDIT] Error logging event: {e}")
            return False
    
    def log_login(self, username: str, success: bool, ip_address: str = None) -> bool:
        """Log a login attempt."""
        details = {
            "success": success,
            "ip_address": ip_address
        }
        severity = "medium" if success else "high"
        return self.log_event("login", details, username, severity)
    
    def log_logout(self, username: str) -> bool:
        """Log a logout event."""
        return self.log_event("logout", {}, username, "low")
    
    def log_credential_access(self, credential_name: str, username: str = "system") -> bool:
        """Log credential vault access."""
        details = {"credential": credential_name}
        return self.log_event("credential_access", details, username, "low")
    
    def log_credential_modify(self, credential_name: str, change_type: str, 
                             username: str = "system") -> bool:
        """Log credential modification."""
        details = {"credential": credential_name, "change_type": change_type}
        return self.log_event("credential_modify", details, username, "high")
    
    def log_credential_rotate(self, credential_name: str, username: str = "system") -> bool:
        """Log credential rotation."""
        details = {"credential": credential_name}
        return self.log_event("credential_rotate", details, username, "medium")
    
    def log_api_call(self, api_name: str, endpoint: str, method: str = "GET",
                    status_code: int = 200, username: str = "system") -> bool:
        """Log an API call."""
        details = {
            "api": api_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code
        }
        severity = "low" if status_code < 400 else "medium"
        return self.log_event("api_call", details, username, severity)
    
    def log_error(self, error_type: str, message: str, context: Dict = None,
                 username: str = "system") -> bool:
        """Log an error event."""
        details = {
            "error_type": error_type,
            "message": message,
            "context": context or {}
        }
        return self.log_event("error", details, username, "high")
    
    def log_suspicious_activity(self, activity_type: str, description: str,
                               severity: str = "high") -> bool:
        """Log suspicious activity."""
        details = {
            "activity_type": activity_type,
            "description": description
        }
        return self.log_event("suspicious_activity", details, "system", severity)
    
    def get_events(self, event_type: str = None, severity: str = None,
                  username: str = None, limit: int = 100) -> List[Dict]:
        """
        Get filtered audit events.
        
        Args:
            event_type: Filter by event type
            severity: Filter by severity level
            username: Filter by username
            limit: Maximum number of events to return
        
        Returns:
            List of filtered events
        """
        events = self.events_in_memory
        
        if event_type:
            events = [e for e in events if e['event_type'] == event_type]
        if severity:
            events = [e for e in events if e['severity'] == severity]
        if username:
            events = [e for e in events if e['username'] == username]
        
        return events[-limit:]
    
    def get_events_by_date(self, start_date: str = None, end_date: str = None,
                          limit: int = 100) -> List[Dict]:
        """
        Get events within a date range (ISO format).
        
        Args:
            start_date: Start date (ISO format, e.g., "2026-02-08")
            end_date: End date (ISO format)
            limit: Maximum events to return
        
        Returns:
            List of events in date range
        """
        events = self.events_in_memory
        
        if start_date:
            events = [e for e in events if e['timestamp'] >= start_date]
        if end_date:
            events = [e for e in events if e['timestamp'] <= end_date]
        
        return events[-limit:]
    
    def get_critical_events(self, hours: int = 24) -> List[Dict]:
        """Get critical events from the last N hours."""
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        return [e for e in self.events_in_memory 
                if e['severity'] == 'critical' and e['timestamp'] >= cutoff_time]
    
    def export_logs(self, filepath: str, format: str = "json") -> bool:
        """
        Export logs to file.
        
        Args:
            filepath: Path to save logs
            format: Export format (json or csv)
        
        Returns:
            True if exported successfully
        """
        try:
            if format == "json":
                with open(filepath, 'w') as f:
                    json.dump(self.events_in_memory, f, indent=2)
            elif format == "csv":
                if not self.events_in_memory:
                    return False
                
                keys = self.events_in_memory[0].keys()
                with open(filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(self.events_in_memory)
            else:
                return False
            
            print_lg(f"[AUDIT] Exported {len(self.events_in_memory)} events to {filepath}")
            return True
            
        except Exception as e:
            print_lg(f"[AUDIT] Error exporting logs: {e}")
            return False
    
    def clear_old_logs(self, days: int = 90) -> bool:
        """
        Clear logs older than N days and rotate log file.
        
        Args:
            days: Keep logs from last N days
        
        Returns:
            True if cleared successfully
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Filter in-memory events
            self.events_in_memory = [e for e in self.events_in_memory 
                                     if e['timestamp'] >= cutoff_date]
            
            # Recreate log file with remaining events
            with open(self.log_file, 'w') as f:
                for event in self.events_in_memory:
                    f.write(json.dumps(event) + '\n')
            
            print_lg(f"[AUDIT] Cleared logs older than {days} days")
            return True
            
        except Exception as e:
            print_lg(f"[AUDIT] Error clearing old logs: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get audit log statistics.
        
        Returns:
            Dict with log statistics
        """
        stats = {
            "total_events": len(self.events_in_memory),
            "events_by_type": {},
            "events_by_severity": {},
            "users_logged": set(),
            "critical_events": 0
        }
        
        for event in self.events_in_memory:
            event_type = event['event_type']
            severity = event['severity']
            username = event['username']
            
            stats["events_by_type"][event_type] = stats["events_by_type"].get(event_type, 0) + 1
            stats["events_by_severity"][severity] = stats["events_by_severity"].get(severity, 0) + 1
            stats["users_logged"].add(username)
            
            if severity == "critical":
                stats["critical_events"] += 1
        
        stats["users_logged"] = list(stats["users_logged"])
        return stats
    
    def health_check(self) -> Dict:
        """
        Check audit logger health.
        
        Returns:
            Dict with health status
        """
        try:
            log_file_exists = os.path.exists(self.log_file)
            log_file_size = os.path.getsize(self.log_file) if log_file_exists else 0
            events_in_memory = len(self.events_in_memory)
            
            return {
                "status": "healthy",
                "log_file_exists": log_file_exists,
                "log_file_size_bytes": log_file_size,
                "events_in_memory": events_in_memory,
                "log_directory": self.log_dir
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
