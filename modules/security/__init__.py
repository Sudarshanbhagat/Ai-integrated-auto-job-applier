"""
Security Module - Phase 3
Encrypted credential storage, secrets rotation, audit logging, account monitoring

Components:
- EncryptedVault: Secure credential storage with encryption
- SecretsManager: Automatic secrets/credential rotation
- AuditLogger: Security event logging and tracking
- AccountMonitor: Account security monitoring and anomaly detection
"""

from modules.security.encrypted_vault import EncryptedVault
from modules.security.secrets_manager import SecretsManager
from modules.security.audit_logger import AuditLogger
from modules.security.account_monitor import AccountMonitor

__all__ = [
    "EncryptedVault",
    "SecretsManager",
    "AuditLogger",
    "AccountMonitor"
]
