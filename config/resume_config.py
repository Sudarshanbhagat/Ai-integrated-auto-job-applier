"""
Resume Configuration
Defines user's resume types, locations, and selection preferences
"""

# ============================================================================
# RESUME TYPES & LOCATIONS
# ============================================================================
# Define which resume files you have and their primary skills
# The bot will use these to intelligently select resumes per job

RESUME_TYPES = {
    # Backend/Server-side focused
    "backend": {
        "path": "resumes/backend.pdf",
        "description": "Backend/Server-side engineer - API, database, systems design focused",
        "primary_skills": ["Python", "Java", "Go", "SQL", "API", "Microservices", "Docker", "AWS"],
        "secondary_skills": ["Database Design", "Linux", "Git", "CI/CD"],
        "avoid_keywords": ["React", "Vue", "Angular", "CSS", "UI/UX", "Frontend"]
    },
    
    # Frontend/UI focused
    "frontend": {
        "path": "resumes/frontend.pdf",
        "description": "Frontend engineer - React, Vue, Angular, UI/UX focused",
        "primary_skills": ["JavaScript", "React", "Vue", "Angular", "TypeScript", "CSS", "HTML", "Frontend", "UI/UX"],
        "secondary_skills": ["Webpack", "Babel", "Node.js", "npm", "Design Systems"],
        "avoid_keywords": ["Backend", "Database", "DevOps", "Infrastructure"]
    },
    
    # Full-stack (generalist)
    "fullstack": {
        "path": "resumes/fullstack.pdf",
        "description": "Full-stack engineer - Both backend and frontend expertise",
        "primary_skills": ["JavaScript", "Python", "React", "Node.js", "API", "Database", "Full-stack"],
        "secondary_skills": ["Docker", "AWS", "Google Cloud", "Azure", "SQL", "MongoDB"],
        "avoid_keywords": []
    },
    
    # DevOps/Infrastructure
    "devops": {
        "path": "resumes/devops.pdf",
        "description": "DevOps/Infrastructure engineer - Cloud, containers, CI/CD",
        "primary_skills": ["Docker", "Kubernetes", "AWS", "GCP", "Azure", "CI/CD", "Terraform", "Ansible", "DevOps"],
        "secondary_skills": ["Python", "Bash", "Linux", "Monitoring", "Infrastructure as Code"],
        "avoid_keywords": ["Frontend", "UI/UX", "Design"]
    },
    
    # Data Science/ML
    "datascience": {
        "path": "resumes/datascience.pdf",
        "description": "Data Scientist/ML engineer - ML models, data analysis",
        "primary_skills": ["Python", "Machine Learning", "Data Science", "TensorFlow", "PyTorch", "Pandas", "SQL", "Statistics"],
        "secondary_skills": ["Deep Learning", "Computer Vision", "NLP", "R", "Scala"],
        "avoid_keywords": ["Frontend", "UI/UX"]
    }
}


# ============================================================================
# VARIANT CONFIGURATION
# ============================================================================
# Resume variants help avoid bot detection by using different formatting

VARIANT_CONFIG = {
    # How many variants to generate per resume type
    "num_variants_per_type": 3,  # 1-5 variants
    
    # Which templates to use for variants
    "templates": ["modern", "classic", "minimal"],
    
    # Rotate variants based on:
    # - "sequential": Use variant 1, 2, 3, 1, 2, 3...
    # - "random": Random variant each time
    # - "time": Different variant at different times of day
    "rotation_strategy": "sequential",
    
    # Minimum time between using the same variant for same job/company
    "variant_min_time_between_repeats_hours": 24,
    
    # Directory to store variants
    "variant_cache_dir": "resumes/variants"
}


# ============================================================================
# SKILL MATCHING CONFIGURATION
# ============================================================================
# How strictly should the bot match job skills to resume selection?

SKILL_MATCHING = {
    # Minimum match score (0.0-1.0) to use a resume without fallback
    "min_match_score": 0.4,
    
    # If no resume matches well, use fallback resume
    "fallback_resume": "fullstack",
    
    # Weight for skill matching algorithm:
    # - "strict": Primary skills must match
    # - "moderate": Secondary skills count for something
    # - "loose": Any skill match is good
    "matching_strategy": "moderate",
    
    # Use LLM for skill extraction (more accurate but slower)
    # If False, uses regex fallback (faster but less accurate)
    "use_llm_extraction": True,
    
    # LLM to use for extraction (if enabled)
    "llm_provider": "openai",  # "openai", "deepseek", "gemini"
}


# ============================================================================
# ATS OPTIMIZATION
# ============================================================================
# Optimize resumes for Applicant Tracking Systems

ATS_CONFIG = {
    # Template to use for ATS optimization
    "ats_template": "classic_ats",
    
    # Ensure resumes are ATS-compatible before uploading
    "validate_ats_compatibility": True,
    
    # Minimum ATS compatibility score (0.0-1.0)
    "min_ats_compatibility_score": 0.8,
    
    # Include keywords from job description in resume
    "keyword_optimization": True,
    
    # Where to add keywords:
    # - "summary": Professional summary
    # - "description": Work experience bullets
    # - "skills": Technical skills section
    # - "all": Distribute across all sections
    "keyword_placement": "summary"
}


# ============================================================================
# RESUME SELECTION PREFERENCES
# ============================================================================
# Fine-tune how resumes are selected

SELECTION_PREFERENCES = {
    # If True, log all selection decisions for analysis
    "log_selections": True,
    
    # Directory to store selection logs
    "log_dir": "logs/resume_selections",
    
    # Prefer certain resume types if match is close
    # Format: {"backend": 1.1, "frontend": 0.9}  (multiplier)
    "preference_weights": {
        "fullstack": 1.0,  # Neutral
        "backend": 1.0,
        "frontend": 1.0,
        "devops": 0.9,  # Slightly deprioritize
        "datascience": 0.8  # More deprioritizing
    },
    
    # Track which resume was used last for this job/company
    # to avoid using the same resume twice for same target
    "avoid_repeat_for_same_target": True,
    
    # Minimum time between using same resume for similar jobs
    "resume_min_time_between_similar_jobs_hours": 4
}


# ============================================================================
# ADVANCED CONFIGURATION
# ============================================================================

ADVANCED = {
    # Cache skill extractions to speed up selection
    "cache_skill_extractions": True,
    "cache_ttl_minutes": 60,
    
    # Validate that resume files actually exist on disk
    "validate_files_on_startup": True,
    
    # Auto-generate variants on startup if missing
    "auto_generate_missing_variants": False,
    
    # Enable resume A/B testing
    "ab_testing_enabled": False,
    "ab_test_sample_rate": 0.1  # 10% of jobs
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_resume_types():
    """Get list of all configured resume types."""
    return list(RESUME_TYPES.keys())


def get_resume_path(resume_type):
    """Get file path for a resume type."""
    if resume_type in RESUME_TYPES:
        return RESUME_TYPES[resume_type]["path"]
    return None


def validate_config():
    """Validate configuration is correct."""
    issues = []
    
    # Check that fallback resume exists
    fallback = SKILL_MATCHING.get("fallback_resume", "fullstack")
    if fallback not in RESUME_TYPES:
        issues.append(f"Fallback resume '{fallback}' not configured")
    
    # Check that resume files exist
    import os
    for resume_type, config in RESUME_TYPES.items():
        path = config.get("path")
        if not os.path.exists(path):
            issues.append(f"Resume file not found: {resume_type} ({path})")
    
    # Check match score is valid
    min_score = SKILL_MATCHING.get("min_match_score", 0.4)
    if not 0.0 <= min_score <= 1.0:
        issues.append("min_match_score must be between 0.0 and 1.0")
    
    # Check ATS score is valid
    min_ats = ATS_CONFIG.get("min_ats_compatibility_score", 0.8)
    if not 0.0 <= min_ats <= 1.0:
        issues.append("min_ats_compatibility_score must be between 0.0 and 1.0")
    
    return issues


# Validate config on import
_config_issues = validate_config()
if _config_issues:
    print("[RESUME_CONFIG] Configuration issues detected:")
    for issue in _config_issues:
        print(f"  ⚠ {issue}")


# ============================================================================
# EXAMPLE RESUME STRUCTURE (for reference)
# ============================================================================
# 
# Your resume files should follow this structure:
#
# CONTACT INFO
# Full Name | Email | Phone | LinkedIn URL
#
# PROFESSIONAL SUMMARY
# 2-3 sentence overview of your background and key strengths
#
# TECHNICAL SKILLS
# Languages: Python, JavaScript, Java
# Frameworks: React, Django, Spring
# Databases: PostgreSQL, MongoDB, Redis
# Tools & Platforms: Docker, AWS, Git
#
# WORK EXPERIENCE
# Company Name | Job Title | Month Year - Month Year
# - Achieved X metric by implementing Y technology
# - Led Z initiative resulting in A% improvement
# - [... 3-5 impact-focused bullets per role ...]
#
# EDUCATION
# Degree Name | University | Graduation Year
# GPA: X.XX (if 3.5+)
#
# CERTIFICATIONS (optional)
# Certification Name | Issuing Body | Year
#
# ============================================================================
