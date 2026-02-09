"""
PHASE 1 IMPLEMENTATION GUIDE
Enterprise Safety, Stealth & Scheduler Layer Integration

This document explains how to integrate the new PHASE 1 safety modules into the existing codebase
while maintaining backward compatibility with existing configurations.

Generated: 2026-02-08
Target Integration: runAiBot.py and config system
"""

################################################################################
# PHASE 1 - NEW MODULES CREATED
################################################################################

NEW FILES:
├── modules/safety/
│   ├── __init__.py
│   ├── constants.py              # All timing and configuration constants
│   ├── scheduler.py              # Session timing & jitter (80 lines)
│   ├── rate_limiter.py           # Daily quotas & adaptive backoff (180 lines)
│   ├── stealth_engine.py         # Anti-detection layer (250 lines)
│   └── behavioral_heuristics.py  # Human-like behavior (350 lines)
│
├── modules/detection/
│   └── __init__.py               # Skip engine for challenges (200 lines)
│
├── modules/state/
│   ├── __init__.py
│   └── session_state.py          # State persistence (150 lines)
│
└── config/
    └── safety_config.py          # User-customizable safety settings (NEW)

TOTAL NEW CODE: ~1,500 lines
BACKWARD COMPATIBILITY: 100% - existing code unchanged


################################################################################
# INTEGRATION CHECKPOINTS
################################################################################

CHECKPOINT 1: Module Availability Test
─────────────────────────────────────────
Add to runAiBot.py (line 40+, after other imports):

    try:
        from modules.safety import Scheduler, RateLimiter, StealthEngine, BehavioralHeuristics
        from modules.detection import SkipEngine
        from modules.state import SessionState
        SAFETY_MODULES_AVAILABLE = True
        print_lg("[SAFETY] All Phase 1 modules loaded successfully")
    except ImportError as e:
        SAFETY_MODULES_AVAILABLE = False
        print_lg(f"[WARNING] Safety modules not available: {e}")

CHECKPOINT 2: Safety Config Import
───────────────────────────────────
Add to runAiBot.py (after config imports):

    try:
        from config.safety_config import (
            enable_scheduler, enable_rate_limiting, enable_stealth_engine,
            enable_behavioral_heuristics, enable_skip_engine,
            max_daily_applications, enable_session_persistence
        )
    except ImportError:
        print_lg("[WARNING] safety_config.py not found, using defaults")
        enable_scheduler = False
        enable_rate_limiting = False
        enable_stealth_engine = False
        enable_behavioral_heuristics = False
        enable_skip_engine = False

CHECKPOINT 3: Initialize Safety Managers
─────────────────────────────────────────
Add to main() function (after driver creation, before login):

    # Initialize safety managers (Phase 1)
    scheduler = None
    rate_limiter = None
    stealth_engine = None
    behavior = None
    skip_engine = None
    session_state = None
    
    if SAFETY_MODULES_AVAILABLE:
        if enable_scheduler:
            scheduler = Scheduler()
            scheduler.start_session()
        
        if enable_rate_limiting:
            rate_limiter = RateLimiter()
        
        if enable_stealth_engine:
            stealth_engine = StealthEngine()
            stealth_engine.configure_chrome_options(options)  # options from createChromeSession()
            stealth_engine.inject_stealth_scripts(driver)
        
        if enable_behavioral_heuristics:
            behavior = BehavioralHeuristics()
        
        if enable_skip_engine:
            skip_engine = SkipEngine()
        
        if enable_session_persistence:
            session_state = SessionState()
            if session_state.state.get("is_crashed"):
                print_lg(f"[RECOVERY] Resuming from crash: {session_state.state.get('crash_reason')}")
                session_state.mark_recovered()


################################################################################
# KEY INTEGRATION POINTS
################################################################################

INTEGRATION POINT #1: Check Active Window Before Starting
──────────────────────────────────────────────────────────
In main() function, after initialization:

    if scheduler and not scheduler.is_active_window():
        scheduler.wait_until_active_window()


INTEGRATION POINT #2: Wait for Rate Limit Delay
────────────────────────────────────────────────
In apply_to_jobs() loop, inside job processing (before answering questions):

    if rate_limiter:
        rate_limiter.wait_before_next_application()


INTEGRATION POINT #3: Check Skip Conditions
──────────────────────────────────────────────
In apply_to_jobs() loop, after get_job_main_details():

    if skip_engine:
        # Check for external platforms
        should_skip, reason = skip_engine.should_skip_platform(job_link, about_company_text)
        if should_skip:
            print_lg(f"[SKIP] {reason}")
            discard_job()
            skip_count += 1
            continue
        
        # Check for challenges
        should_skip, challenge = skip_engine.should_skip_due_to_challenge(driver.page_source)
        if should_skip:
            print_lg(f"[SKIP] Challenge detected: {challenge}")
            discard_job()
            skip_count += 1
            continue


INTEGRATION POINT #4: Record Application Success
─────────────────────────────────────────────────
In submitted_jobs() function (after successful application logging):

    if rate_limiter:
        rate_limiter.record_application()
    
    if scheduler:
        scheduler.record_application()
    
    if session_state:
        session_state.record_application(job_id)


INTEGRATION POINT #5: Behavioral Heuristics - Pre-Apply Research
─────────────────────────────────────────────────────────────────
In apply_to_jobs() loop, after check_blacklist(), before answer_questions():

    if behavior:
        behavior.research_job_before_applying(driver)
        
        if behavior.should_take_random_break():
            behavior.take_random_pause()


INTEGRATION POINT #6: Behavioral Heuristics - Save vs Apply
────────────────────────────────────────────────────────────
In apply_to_jobs() loop, after getting job description, before form filling:

    if behavior:
        if behavior.should_save_job_instead_of_apply():
            # Click "Save job" instead of "Easy Apply"
            try:
                wait_span_click(driver, "Save", 2)
                external_jobs_count += 1
                continue
            except:
                pass  # Fall through to normal apply


INTEGRATION POINT #7: Daily Quota Check
────────────────────────────────────────
In run() function, at the end before returning:

    if rate_limiter:
        if not rate_limiter.can_apply():
            print_lg("[RATE_LIMIT] Daily quota reached")
            dailyEasyApplyLimitReached = True
            return total_runs


INTEGRATION POINT #8: Crash Recovery
──────────────────────────────────────
In main() function, in the finally block:

    if session_state:
        try:
            session_state.record_skip(f"Session ended")
        except:
            pass


INTEGRATION POINT #9: On Exception/Crash
──────────────────────────────────────────
In main() function except blocks:

    except Exception as e:
        if session_state:
            session_state.mark_crashed(str(e))
        # ... rest of exception handling


################################################################################
# PHASE 1 IMPLEMENTATION CHECKLIST
################################################################################

PRE-IMPLEMENTATION:
  [ ] Read this document completely
  [ ] Understand all 9 integration points
  [ ] Back up runAiBot.py and config/ folder
  [ ] Create git branch: git checkout -b phase1-safety

IMPLEMENTATION PHASE:
  [ ] Copy Phase 1 module files to workspace
  [ ] Copy safety_config.py to config/ folder
  [ ] Add CHECKPOINT 1 test (module import check)
  [ ] Add CHECKPOINT 2 safety config import
  [ ] Add CHECKPOINT 3 initialization
  [ ] Add INTEGRATION POINT #1 (check active window)
  [ ] Add INTEGRATION POINT #2 (wait for delay)
  [ ] Add INTEGRATION POINT #3 (skip checks)
  [ ] Add INTEGRATION POINT #4 (record application)
  [ ] Add INTEGRATION POINT #5 (pre-apply research)
  [ ] Add INTEGRATION POINT #6 (save vs apply)
  [ ] Add INTEGRATION POINT #7 (daily quota)
  [ ] Add INTEGRATION POINT #8 (crash recovery)

TESTING PHASE:
  [ ] Run with safety modules disabled (safety_config: all False)
      - Should work identically to before
      - No changes in behavior
  [ ] Run with only scheduler enabled
      - Should respect active windows
      - Should take micro-breaks
  [ ] Run with only rate limiter enabled
      - Should enforce 2-5 min delays
      - Should respect 50/day limit
  [ ] Run with all Phase 1 features enabled
      - Should combine all behaviors
      - Should not crash

VALIDATION PHASE:
  [ ] Check logs for [SCHEDULER], [RATE_LIMIT], [STEALTH], [BEHAVIOR], [SKIP] messages
  [ ] Verify no duplicate applications
  [ ] Monitor session state file (logs/session_state.json)
  [ ] Test crash recovery (kill process, restart)
  [ ] Verify daily quota resets at midnight

DEPLOYMENT PHASE:
  [ ] Run in non-headless mode overnight for 50 applications
  [ ] Monitor LinkedIn for any unusual activity
  [ ] Check if applications are being received (check LinkedIn inbox)
  [ ] If no issues after 24 hours, mark Phase 1 complete


################################################################################
# SAFETY RECOMMENDATIONS (CRITICAL!)
################################################################################

1. FIRST RUN - START CONSERVATIVE:
   - Set max_daily_applications = 20 (not 50)
   - Test for 3-5 days
   - Gradually increase to 50 if no issues

2. MONITORING INDICATORS:
   ✓ GOOD: Steady 2-5 minute delays between apps
   ✓ GOOD: Daily quota reached around 50 apps
   ✓ GOOD: Micro-breaks every 5 apps (1-3 min each)
   
   ✗ BAD: LinkedIn asking for verification codes
   ✗ BAD: "Unusual activity detected" messages
   ✗ BAD: Jobs not being applied to (but no errors)
   ✗ BAD: Rate limiting detected (429 errors)

3. IF BAD SIGNS APPEAR:
   1. Set vacation_mode = True immediately
   2. Stop running the bot for 48 hours
   3. Log into LinkedIn manually to verify account is OK
   4. Reset backoff_multiplier to 1.0 in logs
   5. Resume with max_daily_applications = 20

4. NEVER:
   ✗ Disable delays to "speed up" - You WILL get banned
   ✗ Skip safety checks for "better results" - Not worth it
   ✗ Set headless_mode = True - Too obvious
   ✗ Run 100+ applications/day - Account death sentence
   ✗ Run without stealth_engine = True - High detection risk


################################################################################
# TESTING PROCEDURE FOR PHASE 1
################################################################################

TEST 1: Module Load Test
─────────────────────────
$ python -c "from modules.safety import Scheduler, RateLimiter; print('✓ Modules load')"

Expected output:
  ✓ Modules load


TEST 2: Default Config Test
──────────────────────────
$ python -c "
from config.safety_config import enable_scheduler, max_daily_applications
print(f'Scheduler enabled: {enable_scheduler}')
print(f'Daily limit: {max_daily_applications}')
"

Expected output:
  Scheduler enabled: True
  Daily limit: 50


TEST 3: Scheduler Timing Test
───────────────────────────────
$ python tests/test_scheduler.py

Expected output:
  [TEST] Active window check: PASS
  [TEST] Jitter calculation: PASS
  [TEST] Micro-break timing: PASS


TEST 4: Rate Limiter Test
──────────────────────────
$ python tests/test_rate_limiter.py

Expected output:
  [TEST] Daily quota enforcement: PASS
  [TEST] Adaptive backoff: PASS
  [TEST] Delay calculation: PASS


TEST 5: Full Integration Test
──────────────────────────────
$ python runAiBot.py --dry-run

Expected output:
  [SAFETY] All Phase 1 modules loaded successfully
  [SCHEDULER] Session started at HH:MM:SS
  [STEALTH] Using user agent: Mozilla/5.0...
  [RATE_LIMIT] Application #1. 49 remaining today.
  ... (continues normally)


################################################################################
# BACKWARD COMPATIBILITY GUARANTEE
################################################################################

✓ All Phase 1 changes are BACKWARD COMPATIBLE

If any safety_config module import fails:
  - Bot defaults to disabling all safety features
  - Existing code runs unchanged
  - behavior is identical to pre-Phase1

Existing config files (personals.py, questions.py, etc.):
  - NO changes required
  - NO breaking changes
  - Fully compatible with Phase 1

How to opt-out of Phase 1:
  1. Set all values to False in config/safety_config.py
  2. OR delete config/safety_config.py (uses defaults)
  3. Bot continues with original behavior


################################################################################
# GIT WORKFLOW FOR PHASE 1
################################################################################

# Create feature branch
git checkout -b phase1-safety-layer

# At each checkpoint, commit:
git add modules/safety/ modules/detection/ modules/state/ config/safety_config.py
git commit -m "Phase 1: Add safety modules (checkpoint 1 - module creation)"

# After integration in runAiBot.py:
git add runAiBot.py
git commit -m "Phase 1: Integrate safety modules into main automation loop"

# After testing:
git add tests/
git commit -m "Phase 1: Add test suite and validation"

# Ready to merge:
git checkout main
git merge --no-ff phase1-safety-layer
git tag -a v1.1.0-phase1 -m "Safety & Stealth improvements"


################################################################################
# NEXT STEPS (PHASE 2)
################################################################################

After Phase 1 is stable (3-5 days of no issues), proceed to:

PHASE 2: Resume Intelligence & Advanced Features
  - Multi-resume selector
  - Resume skill extraction
  - Variant generation
  - ATS-safe formatting

Timeline: Week 2-3
Effort: 20-30 hours of development


################################################################################
# SUPPORT & TROUBLESHOOTING
################################################################################

Issue: "ModuleNotFoundError: No module named 'modules.safety'"
Solution:
  1. Verify files in modules/safety/ directory exist
  2. Ensure __init__.py files exist
  3. Run: python -m pip install --upgrade setuptools

Issue: "Safety config not found"
Solution:
  1. Create config/safety_config.py (provided in this delivery)
  2. Copy to config/ folder exactly
  3. Run: python -c "from config.safety_config import *"

Issue: "Session state file permission error"
Solution:
  1. Ensure logs/ directory exists
  2. Run: mkdir -p logs/
  3. Run:chmod 755 logs/

For more help:
  - GitHub Issues: https://github.com/GodsScion/Auto_job_applier_linkedIn/issues
  - Discord: https://discord.gg/fFp7uUzWCY
  - Check logs/error.log for detailed error messages

################################################################################
"""
