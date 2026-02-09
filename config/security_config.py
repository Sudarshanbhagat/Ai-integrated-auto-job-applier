"""
Phase 3 Security Configuration
Manages security features: encrypted vault, secrets rotation, audit logging, account monitoring
"""

# ============================================================================
# ENCRYPTED VAULT CONFIGURATION
# ============================================================================

VAULT_CONFIG = {
    # Path to encrypted vault file
    "vault_file": "config/.vault",
    
    # Use encryption (requires 'cryptography' library)
    # Install with: pip install cryptography
    "enable_encryption": True,
    
    # Master password source
    # Options: "env_var" (from VAULT_MASTER_PASSWORD env var), "file", "prompt"
    "master_password_source": "env_var",
    
    # File permissions for vault (Unix only)
    "vault_file_permissions": 0o600,  # Read/write owner only
    
    # Credentials to store in vault
    "credentials_to_store": {
        "linkedin_username": {"type": "username", "expires_days": None},
        "linkedin_password": {"type": "password", "expires_days": None},
        "openai_api_key": {"type": "api_key", "expires_days": 365},
        "deepseek_api_key": {"type": "api_key", "expires_days": 365},
        "gemini_api_key": {"type": "api_key", "expires_days": 365},
    }
}


# ============================================================================
# SECRETS ROTATION CONFIGURATION
# ============================================================================

SECRETS_ROTATION = {
    # Enable automatic secrets rotation
    "enable_rotation": True,
    
    # Check for due rotations every N hours
    "check_interval_hours": 24,
    
    # Secrets to rotate and their rotation periods
    "secrets": {
        "openai_api_key": {
            "rotation_days": 90,
            "auto_rotate": False,  # Manual rotation required
            "enabled": True
        },
        "deepseek_api_key": {
            "rotation_days": 90,
            "auto_rotate": False,
            "enabled": True
        },
        "gemini_api_key": {
            "rotation_days": 90,
            "auto_rotate": False,
            "enabled": True
        },
        "linkedin_session_token": {
            "rotation_days": 30,
            "auto_rotate": True,
            "enabled": True
        }
    },
    
    # Keep backup of old secrets for rollback
    "keep_backups": True,
    "max_backup_versions": 3
}


# ============================================================================
# AUDIT LOGGING CONFIGURATION
# ============================================================================

AUDIT_LOGGING = {
    # Enable audit logging
    "enable_audit_logging": True,
    
    # Directory to store audit logs
    "log_directory": "logs/security/audit",
    
    # Log file rotation
    "rotate_daily": True,
    "max_log_files": 90,  # Keep 90 days of logs
    
    # Events to log
    "log_events": {
        "logins": True,
        "credential_access": True,
        "credential_modifications": True,
        "api_calls": True,
        "errors": True,
        "suspicious_activity": True,
        "account_changes": True,
        "policy_violations": True
    },
    
    # Alert on high severity events
    "alert_on_severity": ["high", "critical"],
    
    # Log format: "json" or "csv"
    "log_format": "json",
    
    # Retention policy
    "retention_days": 90
}


# ============================================================================
# ACCOUNT MONITORING CONFIGURATION
# ============================================================================

ACCOUNT_MONITORING = {
    # Enable account monitoring
    "enable_monitoring": True,
    
    # Directory to store monitoring data
    "monitor_directory": "logs/security/account",
    
    # Activity thresholds for anomaly detection
    "thresholds": {
        "max_applications_per_hour": 20,
        "max_login_attempts_per_hour": 5,
        "max_failed_logins_per_day": 3,
        "max_errors_per_hour": 5,
        "unusual_login_location_timeout_hours": 24,
        "unusual_application_hours": (0, 5)  # Hours 0-5 AM
    },
    
    # Anomaly detection rules
    "detect_anomalies": {
        "burst_activity": True,
        "location_changes": True,
        "timing_anomalies": True,
        "error_spikes": True,
        "repeated_failures": True
    },
    
    # Alert thresholds
    "alert_on_anomalies": True,
    "anomaly_alert_cooldown_hours": 1  # Wait 1 hour before alerting on same anomaly
}


# ============================================================================
# SECURITY POLICIES
# ============================================================================

SECURITY_POLICIES = {
    # Password policy
    "password_policy": {
        "min_length": 12,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special_chars": True,
        "expiration_days": 90
    },
    
    # API key policy
    "api_key_policy": {
        "rotation_days": 90,
        "min_key_length": 32,
        "restrict_key_usage_scope": True
    },
    
    # Session policy
    "session_policy": {
        "max_session_duration_hours": 24,
        "idle_timeout_minutes": 30,
        "require_re_authentication_for_sensitive_ops": True,
        "single_session_per_user": True
    },
    
    # IP masking/VPN
    "network_policy": {
        "allow_vpn": False,
        "allow_proxy": False,
        "allowed_countries": ["US"],  # Empty = all countries allowed
        "block_suspicious_ips": True
    },
    
    # 2FA
    "mfa_policy": {
        "require_mfa": False,
        "mfa_methods": ["authenticator", "sms"],
        "mfa_grace_period_days": 7
    }
}


# ============================================================================
# INTEGRATION SETTINGS
# ============================================================================

SECURITY_INTEGRATION = {
    # Enable Phase 3 Security features in runAiBot.py
    "enable_encrypted_vault": True,
    "enable_secrets_manager": True,
    "enable_audit_logger": True,
    "enable_account_monitor": True,
    
    # Security startup checks
    "run_security_checks_on_startup": True,
    
    # Health check interval (hours)
    "health_check_interval_hours": 1,
    
    # Backup important config/state files
    "backup_important_files": True,
    "backup_directory": "backups/security",
    "backup_frequency_hours": 24
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_enabled_security_features():
    """Get list of enabled security features."""
    features = []
    if VAULT_CONFIG["enable_encryption"]:
        features.append("encrypted_vault")
    if SECRETS_ROTATION["enable_rotation"]:
        features.append("secrets_rotation")
    if AUDIT_LOGGING["enable_audit_logging"]:
        features.append("audit_logging")
    if ACCOUNT_MONITORING["enable_monitoring"]:
        features.append("account_monitoring")
    return features


def validate_security_config():
    """Validate security configuration."""
    issues = []
    
    # Check vault config
    if VAULT_CONFIG["enable_encryption"]:
        try:
            import cryptography
        except ImportError:
            issues.append("cryptography library not installed. Install with: pip install cryptography")
    
    # Check vault master password source
    if VAULT_CONFIG["master_password_source"] == "env_var":
        import os
        if not os.environ.get("VAULT_MASTER_PASSWORD"):
            issues.append("VAULT_MASTER_PASSWORD environment variable not set")
    
    # Check directories exist or can be created
    import os
    for key, config in [
        ("vault", VAULT_CONFIG),
        ("audit", AUDIT_LOGGING),
        ("monitor", ACCOUNT_MONITORING)
    ]:
        if "directory" in config:
            dir_path = config["directory"]
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create {key} directory {dir_path}: {e}")
    
    return issues


# Validate on import
_config_issues = validate_security_config()
if _config_issues:
    print("[SECURITY_CONFIG] Configuration issues detected:")
    for issue in _config_issues:
        print(f"  ⚠ {issue}")
