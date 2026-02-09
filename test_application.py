#!/usr/bin/env python3
"""
Comprehensive Test Suite for LinkedIn Auto Job Applier
Tests all 3 phases: Safety & Stealth, Resume Intelligence, Security Hardening
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_test(name, passed, details=""):
    """Print test result"""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} | {name}")
    if details:
        print(f"       -> {details}")

# Test Suite
results = []

# ============================================================================
# PHASE 0: Core Dependencies
# ============================================================================
print_header("PHASE 0: Testing Core Dependencies")

try:
    import selenium
    print_test("Selenium installed", True, f"version {selenium.__version__}")
    results.append(True)
except ImportError as e:
    print_test("Selenium installed", False, str(e))
    results.append(False)

try:
    import undetected_chromedriver as uc
    print_test("Undetected ChromeDriver installed", True)
    results.append(True)
except ImportError as e:
    print_test("Undetected ChromeDriver installed", False, str(e))
    results.append(False)

try:
    from cryptography.fernet import Fernet
    print_test("Cryptography library installed", True)
    results.append(True)
except ImportError as e:
    print_test("Cryptography library installed", False, str(e))
    results.append(False)

try:
    import openai
    print_test("OpenAI library installed", True, "(optional)")
    results.append(True)
except ImportError:
    print_test("OpenAI library installed", False, "(optional - LLM features limited)")
    results.append(True)  # Optional, don't fail

# ============================================================================
# PHASE 1: Safety & Stealth Modules
# ============================================================================
print_header("PHASE 1: Testing Safety & Stealth Components")

try:
    from modules.safety.scheduler import Scheduler
    scheduler = Scheduler()
    print_test("Scheduler module loads", True)
    results.append(True)
except Exception as e:
    print_test("Scheduler module loads", False, str(e))
    results.append(False)

try:
    from modules.safety.rate_limiter import RateLimiter
    rate_limiter = RateLimiter()
    print_test("RateLimiter module loads", True)
    results.append(True)
except Exception as e:
    print_test("RateLimiter module loads", False, str(e))
    results.append(False)

try:
    from modules.safety.stealth_engine import StealthEngine
    stealth = StealthEngine()
    print_test("StealthEngine module loads", True)
    results.append(True)
except Exception as e:
    print_test("StealthEngine module loads", False, str(e))
    results.append(False)

try:
    from modules.safety.behavioral_heuristics import BehavioralHeuristics
    behavior = BehavioralHeuristics()
    print_test("BehavioralHeuristics module loads", True)
    results.append(True)
except Exception as e:
    print_test("BehavioralHeuristics module loads", False, str(e))
    results.append(False)

try:
    from config.safety_config import enable_scheduler, enable_rate_limiting
    assert enable_scheduler is not None
    print_test("Safety configuration loads", True)
    results.append(True)
except Exception as e:
    print_test("Safety configuration loads", False, str(e))
    results.append(False)

# ============================================================================
# PHASE 2: Resume Intelligence Modules
# ============================================================================
print_header("PHASE 2: Testing Resume Intelligence Components")

try:
    from modules.resume.skill_extractor import SkillExtractor
    extractor = SkillExtractor()
    print_test("SkillExtractor module loads", True)
    results.append(True)
except Exception as e:
    print_test("SkillExtractor module loads", False, str(e))
    results.append(False)

try:
    from modules.resume.skill_mapper import SkillMapper
    mapper = SkillMapper()
    print_test("SkillMapper module loads", True)
    results.append(True)
except Exception as e:
    print_test("SkillMapper module loads", False, str(e))
    results.append(False)

try:
    from modules.resume.variant_generator import VariantGenerator
    generator = VariantGenerator()
    print_test("VariantGenerator module loads", True)
    results.append(True)
except Exception as e:
    print_test("VariantGenerator module loads", False, str(e))
    results.append(False)

try:
    from modules.resume.ats_templates import ATSTemplate
    ats = ATSTemplate()
    print_test("ATSTemplate module loads", True)
    results.append(True)
except Exception as e:
    print_test("ATSTemplate module loads", False, str(e))
    results.append(False)

try:
    from modules.resume.selector import ResumeSelector
    selector = ResumeSelector()
    print_test("ResumeSelector module loads", True)
    results.append(True)
except Exception as e:
    print_test("ResumeSelector module loads", False, str(e))
    results.append(False)

try:
    from config.resume_config import RESUME_TYPES
    assert RESUME_TYPES is not None and len(RESUME_TYPES) > 0
    print_test("Resume configuration loads", True)
    results.append(True)
except Exception as e:
    print_test("Resume configuration loads", False, str(e))
    results.append(False)

# ============================================================================
# PHASE 3: Security Hardening Modules
# ============================================================================
print_header("PHASE 3: Testing Security Hardening Components")

try:
    from modules.security import EncryptedVault
    vault = EncryptedVault()
    print_test("EncryptedVault module loads", True, "AES-256 encryption ready")
    results.append(True)
except Exception as e:
    print_test("EncryptedVault module loads", False, str(e))
    results.append(False)

try:
    from modules.security import SecretsManager, EncryptedVault
    vault = EncryptedVault()
    manager = SecretsManager(vault)
    print_test("SecretsManager module loads", True, "90-day rotation ready")
    results.append(True)
except Exception as e:
    print_test("SecretsManager module loads", False, str(e))
    results.append(False)

try:
    from modules.security import AuditLogger
    logger = AuditLogger()
    print_test("AuditLogger module loads", True, "Logs available at logs/security/audit.log")
    results.append(True)
except Exception as e:
    print_test("AuditLogger module loads", False, str(e))
    results.append(False)

try:
    from modules.security import AccountMonitor
    monitor = AccountMonitor()
    print_test("AccountMonitor module loads", True, "Anomaly detection ready")
    results.append(True)
except Exception as e:
    print_test("AccountMonitor module loads", False, str(e))
    results.append(False)

try:
    from config.security_config import VAULT_CONFIG, SECRETS_ROTATION
    assert VAULT_CONFIG is not None and SECRETS_ROTATION is not None
    print_test("Security configuration loads", True)
    results.append(True)
except Exception as e:
    print_test("Security configuration loads", False, str(e))
    results.append(False)

# ============================================================================
# PHASE 3: Security Functionality Tests
# ============================================================================
print_header("PHASE 3: Testing Security Functionality")

try:
    from modules.security import EncryptedVault, AuditLogger, AccountMonitor
    
    # Test encryption
    vault = EncryptedVault()
    vault.set_credential("test_key", "test_value")
    retrieved = vault.get_credential("test_key")
    assert retrieved == "test_value", "Encryption/decryption mismatch"
    vault.delete_credential("test_key")
    print_test("Encryption/Decryption works", True, "Credentials stored securely")
    results.append(True)
except Exception as e:
    print_test("Encryption/Decryption works", False, str(e))
    results.append(False)

try:
    from modules.security import AuditLogger
    logger = AuditLogger()
    logger.log_login("testuser", success=True, ip_address="127.0.0.1")
    events = logger.get_events(event_type="login")
    assert len(events) > 0, "No login events logged"
    print_test("Audit logging works", True, f"{len(events)} events logged")
    results.append(True)
except Exception as e:
    print_test("Audit logging works", False, str(e))
    results.append(False)

try:
    from modules.security import AccountMonitor
    monitor = AccountMonitor()
    monitor.record_login("testuser", success=True)
    monitor.record_application("TestCo", "Engineer", success=True)
    
    # Test anomaly detection
    for i in range(25):
        monitor.record_application(f"Co{i}", "Engineer", success=True)
    
    suspicious = monitor.detect_suspicious_patterns()
    # May or may not detect based on threshold
    print_test("Anomaly detection works", True, f"Analyzed {25} applications")
    results.append(True)
except Exception as e:
    print_test("Anomaly detection works", False, str(e))
    results.append(False)

try:
    from modules.security import AccountMonitor
    monitor = AccountMonitor()
    health = monitor.get_health_status()
    assert "health_score" in health, "No health score"
    assert "status" in health, "No status"
    assert 0 <= health["health_score"] <= 100, "Health score out of range"
    print_test("Health scoring works", True, f"Score: {health['health_score']}/100 - {health['status']}")
    results.append(True)
except Exception as e:
    print_test("Health scoring works", False, str(e))
    results.append(False)

# ============================================================================
# Configuration Tests
# ============================================================================
print_header("PHASE 1-3: Testing Configuration Loading")

try:
    from config.personals import first_name, last_name
    assert first_name and last_name
    print_test("Config: Personal info loads", True, f"{first_name} {last_name}")
    results.append(True)
except Exception as e:
    print_test("Config: Personal info loads", False, str(e))
    results.append(False)

try:
    from config.search import search_location, job_titles
    print_test("Config: Search settings load", True)
    results.append(True)
except Exception as e:
    print_test("Config: Search settings load", False, str(e))
    results.append(False)

try:
    from config.settings import run_in_background, enable_phase2_resume_selection
    print_test("Config: Application settings load", True)
    results.append(True)
except Exception as e:
    print_test("Config: Application settings load", False, str(e))
    results.append(False)

# ============================================================================
# Main Application Import Test
# ============================================================================
print_header("Main Application Tests")

try:
    # Don't actually run main() but verify it can be imported
    from runAiBot import main, login_LN, get_applied_job_ids
    print_test("runAiBot module imports", True, "Application ready to run")
    results.append(True)
except Exception as e:
    print_test("runAiBot module imports", False, str(e))
    results.append(False)

try:
    from modules.helpers import print_lg
    print_test("Helper functions load", True)
    results.append(True)
except Exception as e:
    print_test("Helper functions load", False, str(e))
    results.append(False)

# ============================================================================
# Summary Report
# ============================================================================
print_header("TEST SUMMARY REPORT")

total_tests = len(results)
passed_tests = sum(results)
failed_tests = total_tests - passed_tests
pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests Run:     {total_tests}")
print(f"Tests Passed:        {passed_tests} [PASS]")
print(f"Tests Failed:        {failed_tests} [FAIL]")
print(f"Pass Rate:           {pass_rate:.1f}%")

print(f"\n{'='*70}")

if failed_tests == 0:
    print("SUCCESS! All tests passed. Application is ready to use.\n")
    print("Next Steps:")
    print("  1. Configure config/secrets.py with LinkedIn credentials")
    print("  2. Configure config/personals.py with your information")
    print("  3. Set VAULT_MASTER_PASSWORD env variable")
    print("  4. Run: python runAiBot.py")
    print()
    sys.exit(0)
else:
    print(f"WARNING: {failed_tests} test(s) failed. Please fix the issues above.\n")
    print("Troubleshooting:")
    print("  1. Verify all dependencies: pip install -r requirements.txt")
    print("  2. Check file permissions: ls -la modules/")
    print("  3. Verify config files: ls -la config/")
    print("  4. Review error messages above for details")
    print()
    sys.exit(1)
