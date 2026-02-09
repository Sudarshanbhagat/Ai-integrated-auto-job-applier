# Quick Start Guide - LinkedIn Auto Job Applier

## Before You Start

You have 3 options:

### Option 1: Run Application Now (Minimal Config)
```powershell
cd e:\Auto_job_applier_linkedIn-main
python runAiBot.py
```
- Will prompt you to login manually if no credentials configured
- Will use existing LinkedIn profile from browser
- Resumes need to be in `resumes/` folder

### Option 2: Full Configuration First (Recommended)
Follow the checklist below, then run the app

### Option 3: Quick Demo Mode
Skip configuration, just see how it works with sample data

---

## Configuration Checklist

### STEP 1: Edit Personal Information
**File**: `config/personals.py`

```python
# Your full name
first_name = "Sai"  
last_name = "Golla"

# Contact info
email = "your.email@example.com"
phone = "123-456-7890"
country = "United States"
state = "California"
city = "San Francisco"
zip_code = "94105"

# Professional summary
summary = "Senior Software Engineer with 5+ years experience..."
```

### STEP 2: Configure Job Search
**File**: `config/search.py`

```python
# What jobs to search for
job_titles = ["Software Engineer", "Backend Developer", "Full Stack Engineer"]

# Where to search
search_location = "San Francisco, CA"

# Additional filters
keywords = ["Python", "AWS", "Docker"]
exclude_keywords = ["Intern", "Freelance", "Part-time"]

# How many to apply for
applications_limit = 50  # per day
```

### STEP 3: Set LinkedIn Credentials (Optional)
**File**: `config/secrets.py`

```python
# Leave blank to use browser's saved profile (recommended for first time)
linkedin_username = ""
linkedin_password = ""

# For OpenAI resume generation (optional)
openai_api_key = ""
```

### STEP 4: Configure Application Answers
**File**: `config/questions.py`

```python
# How to answer common application questions
experience_level = "5+ years"

# Application behavior
pause_before_submit = True  # Review before applying
pause_before_unknowns = True  # Ask about questions the bot doesn't know
```

### STEP 5: Add Your Resumes
**Folder**: `resumes/`

Create these resume files (PDF format):
- `resumes/backend.pdf` - Backend focused
- `resumes/frontend.pdf` - Frontend focused  
- `resumes/fullstack.pdf` - Full-stack version
- `resumes/devops.pdf` - DevOps focused
- `resumes/datascience.pdf` - Data Science focused

Or just put one resume as `default.pdf` and the app will use it for all jobs.

### STEP 6 (Security): Set Master Password
**Optional but recommended**

```powershell
# In PowerShell
$env:VAULT_MASTER_PASSWORD = "your-secure-password-here"

# Or set it permanently:
[System.Environment]::SetEnvironmentVariable('VAULT_MASTER_PASSWORD', 'your-secure-password-here', 'User')
```

This encrypts your stored credentials.

---

## First Run Walkthrough

```powershell
# 1. Navigate to project folder
cd e:\Auto_job_applier_linkedIn-main

# 2. (Optional) Configure the files above

# 3. Run the application
python runAiBot.py

# What happens:
# - Opens Chrome browser automatically
# - Logs into LinkedIn (uses saved profile or asks you)
# - Searches for matching jobs
# - Reviews each job
# - Fills in application form automatically
# - Applies to job (or pauses for your review)
# - Continues to next job
# - Logs all activity
```

---

## View Applied Jobs

After running the application:

```powershell
# Start the dashboard server
python app.py

# Open browser to: http://localhost:5000
# You'll see:
# - Jobs applied to
# - Application success rate
# - Timestamps and details
```

---

## What Each Phase Does

### Phase 1: Safety & Stealth
- ✅ Prevents bot detection
- ✅ Human-like delays between actions
- ✅ Random screen resolutions
- ✅ Auto-skips CAPTCHA/OTP challenges
- ✅ Session recovery if app crashes

### Phase 2: Resume Intelligence  
- ✅ Reads job description
- ✅ Extracts required skills
- ✅ Picks best matching resume
- ✅ Customizes content for job
- ✅ Improves recruiter match

### Phase 3: Security Hardening
- ✅ Encrypts credentials
- ✅ Rotates API keys
- ✅ Logs all activities
- ✅ Detects suspicious patterns
- ✅ Health scoring

---

## Logs & Data

### View Activity Logs
```
logs/security/audit.log  - All security events
logs/errors.log          - Application errors
data/applied_jobs.csv    - Jobs you've applied to
```

### Enable Debug Mode
**File**: `config/settings.py`
```python
debug_mode = True  # More verbose logging
```

---

## Need Help?

### Common Issues:

**"Chrome not found"**
- Undetected-chromedriver will download it
- Make sure you have internet connection
- Wait 1-2 minutes on first run

**"Cannot find 'Log.txt'"**
- Ignore this warning - it's a minor logging issue
- Application still works fine

**"Rate limit error"**
- Phase 1 automatically backs off
- Wait a few hours before next batch
- Prevents LinkedIn account ban

**"Resume not selected"**
- Put resumes in `resumes/` folder
- Name them: backend.pdf, frontend.pdf, etc.
- Or just use `default.pdf`

---

## Configuration Examples

### Example 1: Backend Engineer
```
Job titles: Python Developer, Backend Engineer, DevOps Engineer
Location: San Francisco, CA
Keywords: Python, AWS, Kubernetes, PostgreSQL
Resume: backend.pdf (automatically selected)
```

### Example 2: Full-Stack Developer
```
Job titles: Full Stack Engineer, JavaScript Developer, React Developer
Location: New York, NY
Keywords: JavaScript, React, Node.js, MongoDB
Resumes: fullstack.pdf (primary), frontend.pdf (fallback)
```

### Example 3: Data Scientist
```
Job titles: Data Scientist, Machine Learning Engineer, AI Engineer
Location: Remote
Keywords: Python, TensorFlow, SQL, scikit-learn
Resume: datascience.pdf (automatically selected)
```

---

## Next Steps

Choose one:

**🔵 Option A**: Edit the config files (5-10 minutes)
- Edit `config/personals.py`
- Edit `config/search.py`  
- Add your resumes
- Then run `python runAiBot.py`

**🟡 Option B**: Run with browser's saved profile (fastest)
```powershell
python runAiBot.py
# Just login when Chrome opens, then let it run
```

**🟢 Option C**: Test with demo data first
```powershell
# Coming soon - demo mode
```

---

## Safety Reminders

1. **First Run**: Set `pause_before_submit = True` to review applications
2. **Application Limits**: Start with 10-20 per day, increase gradually
3. **Breaks**: The app automatically takes breaks to seem human
4. **Credentials**: Never hardcode passwords - use `secrets.py` or environment variables
5. **Monitoring**: Check `logs/security/audit.log` for anomalies

---

## You're Ready! 🚀

Your application has been tested and is ready to use. Choose your starting option above and let's get your job applications automated!

Questions? Check TEST_RESULTS.md for detailed test results.
