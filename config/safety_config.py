"""
Safety Configuration - Enterprise-Grade Anti-Detection Settings
User-customizable settings that control all safety, stealth, and behavioral features
"""

###################################################### SCHEDULER SETTINGS ######################################################

# Enable scheduler-based job application timing?
enable_scheduler = True

# Active hours for job applications (when bot is allowed to run)
# Leave in quotes exactly as shown: "HH:MM-HH:MM"
active_windows = [
    "09:00-11:00",  # Morning window
    "13:00-15:00",  # Afternoon window  
    "18:00-21:00",  # Evening window
]

# How much variance (jitter) to apply to window start/end times, in minutes
# Example: if window is 09:00-11:00 with ±22 jitter, actual window is ~08:38-11:22
window_jitter_minutes = 22

# Prevent bot from running between 10 PM and 8 AM?
prevent_night_runs = True

# Take a micro-break (1-3 minutes) after every N applications for human realism
micro_break_every_n_applies = 5

# Treat weekends as "light days" with reduced quota (50% of daily limit)
light_days_on_weekends = True

# Fully disable the bot (vacation mode - leave as False for normal operation)
vacation_mode = False


###################################################### RATE LIMITING & QUOTAS ######################################################

# Enable rate limiting (enforces daily quotas and delays)?
enable_rate_limiting = True

# Maximum number of applications per day
# LinkedIn's soft limit is ~75/day, we use 50 for safety
max_daily_applications = 45

# Minimum seconds between applications (random between min and max)
min_delay_between_applications_sec = 120  # 2 minutes

# Maximum seconds between applications
max_delay_between_applications_sec = 300  # 5 minutes

# Enable adaptive backoff? (Increases delays if we detect rate limiting)
adaptive_backoff_enabled = True

# Multiplier to apply when rate limiting is detected
# Example: if we hit limits, delays become 1.5x longer, then 1.5x longer again, etc.
backoff_multiplier = 1.5

# Maximum delay to use even with backoff (15 minutes max, even if being throttled)
max_backoff_delay_seconds = 900


###################################################### BEHAVIORAL HEURISTICS ######################################################

# Enable realistic human-like behavior patterns?
enable_behavioral_heuristics = True

# Simulate realistic mouse movement before interactions?
human_mouse_movement = True

# Use variable scrolling speeds (like a human would)?
variable_scroll_speed = True

# Read job description before applying (2-20 seconds, includes scrolling)?
pre_apply_research = True

# Probability of taking a random pause (0.0 = never, 1.0 = always)
# 0.08 = 8% chance per application
random_interruption_probability = 0.08

# Duration of random pauses when they happen (min, max in seconds)
random_pause_duration_min_sec = 30
random_pause_duration_max_sec = 180  # 3 minutes

# Probability of saving a job instead of applying to it (avoids applying to all)
save_job_instead_of_apply_probability = 0.15  # 15% of jobs

# Probability of skipping a good job (appears non-robotic)
skip_suitable_job_probability = 0.05  # 5% of suitable jobs

# Probability of adding small typing errors that are then corrected
typo_probability = 0.02  # 2% - very subtle

# Type slowly like a human instead of instantly? (realistic 40-80 WPM)
slow_typing_enabled = True


###################################################### STEALTH & FINGERPRINTING ######################################################

# Enable comprehensive stealth layer (hiding automation indicators)?
enable_stealth_engine = True

# Inject JavaScript to hide navigator.webdriver flag?
hide_navigator_webdriver = True

# Remove ChromeDriver detection strings from browser?
cdc_string_removal = True

# Patch JavaScript to defeat fingerprinting detection?
js_fingerprint_patch = True

# Run Chrome in headless mode? (WARNING: Headless is easily detected - only for testing!)
headless_mode = False

# Rotate user agent on each session? (Avoid same UA every time)
user_agent_rotation = True

# Add noise to canvas fingerprinting to avoid detection?
canvas_noise = True

# Match system timezone so it looks natural?
timezone_matching = True

# Match system language/locale in headers?
language_matching = True

# Vary screen resolution to appear different each time?
screen_resolution_variation = True


###################################################### PLATFORM SKIP ENGINE ######################################################

# Enable automatic skipping of problematic platforms and conditions?
enable_skip_engine = True

# Platforms to skip (external portals we can't automate)
skip_external_platforms = [
    "workday",
    "myworkdayjobs",
    "successfactors",
    "oraclecloud",
    "icims",
    "greenhouse",
    "lever",
    "ashby"
]

# Conditions that should trigger auto-skip (can't handle these)
skip_conditions = [
    "captcha",           # I'm not a robot checks
    "otp",               # One-time password required
    "phone_verification",  # Phone verification needed
    "email_verification",  # Email verification needed
    "assessment",        # Coding or skills assessment
    "video_interview",   # One-way video interview
    "security_challenge"   # Security challenges
]

# Auto-recover from skips (try next job)?
auto_recover_from_skip = True

# Log skip reasons to database for analytics?
log_skips_to_database = True

# Skip jobs already applied to?
skip_already_applied = True

# Skip jobs that look like spam/promoted?
skip_spam_jobs = True

# Skip jobs older than this many hours?
skip_jobs_older_than_hours = 48

# Skip jobs that appear to be reposted (hiring multiple times)?
avoid_reposted_jobs = True


###################################################### LOGGING & OBSERVABILITY ######################################################

# Log level: "DEBUG", "INFO", "WARNING", "ERROR"
log_level = "INFO"

# Sanitize logs (remove passwords, API keys, personal info)?
sanitize_sensitive_data = True

# Log skip reasons for each skipped job?
log_skip_reasons = True

# Log detected challenges?
log_detected_challenges = True

# Take screenshot on errors for debugging?
screenshot_on_error = True

# Automatically delete logs older than this many days?
auto_cleanup_logs_days = 30


###################################################### SESSION PERSISTENCE ######################################################

# Enable session persistence (remember state across crashes)?
enable_session_persistence = True

# Automatically resume from crash/interruption?
auto_resume_on_crash = True

# Number of retries on error before giving up
max_retries_on_error = 3

# Seconds to wait before retrying
retry_delay_seconds = 30


############################################################################################################
"""
SAFETY NOTES:

1. These settings are CRITICAL for account survival. Don't be aggressive!
   - 50 applications/day is safe
   - 75+ applications/day is risky
   - 100+ applications/day will likely trigger bans

2. Minimum delays of 2-5 minutes between applications are not speed-related:
   - The delays allow time for LinkedIn's backend to process
   - Faster applications = more obvious automation
   - Slower = safer + more human-like

3. Behavioral heuristics are NOT optional:
   - Disabling them increases detection risk significantly
   - The 5-15% of jobs we skip/pause for are "noise" that protects the whole account
   - It's worth sacrificing a few applications to keep the account alive

4. Stealth settings:
   - Do NOT use headless mode (it's too obvious)
   - Do enable user agent rotation (changes every session)
   - Do enable fingerprint patching (defeats canvas/WebGL detection)

5. Skip engine:
   - External platforms (Workday, iCIMS) CAN'T be automated safely
   - Challenges (CAPTCHA, OTP) MUST be skipped (no auto-solving)
   - Better to skip 20 jobs than get account banned

6. Active windows:
   - Humans don't apply at 3 AM (LinkedIn's monitoring increases then)
   - Humans apply during business hours
   - The jitter (±22 min) makes patterns look random

EMERGENCY RECOVERY:

If you suspect an account is being monitored:
1. vacation_mode = True (pauses everything)
2. Reduce max_daily_applications to 20
3. Increase min_delay_between_applications_sec to 300+ (5+ min)
4. Take 2-3 day break

If you get 429 (rate limit) errors:
1. adaptive_backoff_enabled automatically activates
2. Delays slowly increase over time
3. Account should recover over ~24 hours
4. Never fight back - just wait!

Questions? Check the GitHub Issues or join Discord for community support.
"""
############################################################################################################
