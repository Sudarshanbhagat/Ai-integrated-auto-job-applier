"""
Resume Selector - Orchestrates intelligent resume selection
Integrates skill extraction, mapping, and variant rotation
"""

from typing import Dict, List, Optional, Tuple
from modules.resume.skill_extractor import SkillExtractor
from modules.resume.skill_mapper import SkillMapper
from modules.resume.variant_generator import VariantGenerator
from modules.helpers import print_lg
import json
import os


class ResumeSelector:
    """
    Main orchestrator for intelligent resume selection.
    
    Workflow:
    1. Extract skills from job description
    2. Map to best resume type
    3. Select variant (rotating through variants)
    4. Log selection reasoning
    """
    
    def __init__(self, resume_config_path: str = "config/resume_config.py"):
        self.skill_extractor = SkillExtractor()
        self.skill_mapper = SkillMapper()
        self.variant_generator = VariantGenerator()
        self.resume_config_path = resume_config_path
        
        # Load resume config
        self.resume_types = {}  # Will be loaded from config
        self.resume_paths = {}  # Map resume type to file path
        self.variant_index = {}  # Track which variant we used last
        
        self._load_config()
        print_lg("[RESUME_SEL] Initialized with resume selection system")
    
    def _load_config(self):
        """Load resume configuration from config file."""
        try:
            # For now, assume a basic structure
            # Full config loading would happen after resume_config.py is created
            self.resume_types = {
                "backend": {"path": "resumes/backend.pdf", "skills": ["python", "java", "database"]},
                "frontend": {"path": "resumes/frontend.pdf", "skills": ["javascript", "react", "css"]},
                "fullstack": {"path": "resumes/fullstack.pdf", "skills": ["python", "javascript", "react"]},
            }
            print_lg(f"[RESUME_SEL] Loaded {len(self.resume_types)} resume types from config")
        except Exception as e:
            print_lg(f"[RESUME_SEL] Warning: Could not load config: {e}")
            self.resume_types = {}
    
    def select_resume(self, job_description: str, job_title: str = "",
                     company: str = "") -> Tuple[Optional[str], Dict]:
        """
        Select the best resume for a job.
        
        Args:
            job_description: Full job description text
            job_title: Job title (optional, for context)
            company: Company name (optional, for context)
        
        Returns:
            Tuple of (resume_file_path, selection_info dictionary)
            
        Selection info contains:
        - resume_type: Which type was selected
        - match_score: Quality of match (0.0-1.0)
        - variant: Which visual variant was used
        - reason: Explanation of selection
        - fallback: True if using fallback resume
        """
        try:
            # Step 1: Extract skills from job description
            extracted_skills = self.skill_extractor.extract(
                job_description,
                job_title=job_title,
                company=company
            )
            print_lg(f"[RESUME_SEL] Extracted {len(extracted_skills)} skill categories")
            
            # Step 2: Map to best resume type
            available_resumes = list(self.resume_types.keys())
            best_resume_type, match_score = self.skill_mapper.find_best_resume(
                extracted_skills,
                available_resumes
            )
            
            # Step 3: Select variant (rotate through them)
            variant_index = self.variant_index.get(best_resume_type, 0)
            
            # Get variants for this resume type
            if best_resume_type:
                variants = self.variant_generator.get_next_variant(
                    best_resume_type
                )
            else:
                variants = None
            
            # Step 4: Prepare response
            if best_resume_type and best_resume_type in self.resume_types:
                resume_file = self.resume_types[best_resume_type]["path"]
                
                # Rotate variant index for next time
                self.variant_index[best_resume_type] = (variant_index + 1) % 5
                
                selection_info = {
                    "resume_type": best_resume_type,
                    "resume_file": resume_file,
                    "match_score": match_score,
                    "variant": variants or "default",
                    "variant_index": variant_index,
                    "extracted_skills": extracted_skills,
                    "job_title": job_title,
                    "fallback": False,
                    "reason": f"Matched {best_resume_type} resume (score: {match_score:.2f})"
                }
                
                print_lg(f"[RESUME_SEL] Selected '{best_resume_type}' resume (score: {match_score:.2f})")
                return resume_file, selection_info
            else:
                # Fallback to first available resume
                fallback_type = available_resumes[0] if available_resumes else None
                if fallback_type:
                    resume_file = self.resume_types[fallback_type]["path"]
                    selection_info = {
                        "resume_type": fallback_type,
                        "resume_file": resume_file,
                        "match_score": 0.0,
                        "variant": None,
                        "extracted_skills": extracted_skills,
                        "job_title": job_title,
                        "fallback": True,
                        "reason": "Using fallback resume (no clear match)"
                    }
                    print_lg(f"[RESUME_SEL] Used fallback resume: {fallback_type}")
                    return resume_file, selection_info
                else:
                    print_lg("[RESUME_SEL] ERROR: No resume types configured!")
                    return None, {"error": "No resume types available"}
        
        except Exception as e:
            print_lg(f"[RESUME_SEL] Error selecting resume: {e}")
            return None, {"error": str(e)}
    
    def suggest_resume_type(self, job_title: str, company: str = "") -> Tuple[str, str]:
        """
        Suggest a resume type based on job title alone (for quick matching).
        
        Returns:
            Tuple of (resume_type, reason)
        """
        job_title_lower = job_title.lower()
        
        # Quick keyword matching
        if any(kw in job_title_lower for kw in ["backend", "api", "server", "database"]):
            return "backend", "Job title indicates backend role"
        elif any(kw in job_title_lower for kw in ["frontend", "ui", "ux", "react", "vue"]):
            return "frontend", "Job title indicates frontend role"
        elif any(kw in job_title_lower for kw in ["fullstack", "full-stack"]):
            return "fullstack", "Job title explicitly mentions fullstack"
        elif any(kw in job_title_lower for kw in ["devops", "infrastructure", "cloud"]):
            return "backend", "DevOps role -> backend resume"
        elif any(kw in job_title_lower for kw in ["embedded", "hardware", "firmware"]):
            return "backend", "Embedded role -> using available resume"
        else:
            return "fullstack", "Default to fullstack for general roles"
    
    def get_selection_history(self, limit: int = 10) -> List[Dict]:
        """Get recent resume selections (if logging is enabled)."""
        # This would be populated by a logging/persistence layer
        return []
    
    def add_resume_type(self, type_name: str, file_path: str, 
                       keywords: List[str] = None):
        """
        Add a new resume type to the system.
        
        Args:
            type_name: Name of resume type
            file_path: Path to resume file
            keywords: List of skill keywords for matching
        """
        if type_name not in self.resume_types:
            self.resume_types[type_name] = {
                "path": file_path,
                "skills": keywords or []
            }
            self.variant_index[type_name] = 0
            print_lg(f"[RESUME_SEL] Added resume type: {type_name}")
    
    def validate_resumes(self) -> Dict[str, bool]:
        """
        Validate that all configured resumes exist.
        
        Returns:
            Dict mapping resume types to validity (True/False)
        """
        validation = {}
        for resume_type, config in self.resume_types.items():
            exists = os.path.exists(config["path"])
            validation[resume_type] = exists
            
            if not exists:
                print_lg(f"[RESUME_SEL] Warning: Resume not found: {config['path']}")
        
        return validation
    
    def get_resume_statistics(self) -> Dict:
        """Get stats on resume usage."""
        return {
            "configured_types": len(self.resume_types),
            "variant_indices": self.variant_index.copy(),
            "total_variants": sum(5 for _ in self.resume_types)  # 5 per type
        }
