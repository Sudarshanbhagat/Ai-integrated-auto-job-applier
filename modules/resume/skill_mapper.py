"""
Skill Mapper - Maps job skills to resume types
Determines which resume is best for a given job
"""

from typing import Dict, List, Tuple, Optional
from modules.helpers import print_lg


class SkillMapper:
    """
    Maps job requirements to resume types.
    
    Resume types:
    - backend: Python, Java, Go, databases, APIs
    - frontend: JavaScript, React, Vue, CSS
    - fullstack: Both backend + frontend
    - embedded: C, C++, hardware, IoT
    - devops: Docker, Kubernetes, CI/CD, AWS
    - cybersecurity: Security, pentesting, compliance
    """
    
    # Define which skills belong to which resume type
    RESUME_TYPE_KEYWORDS = {
        "backend": {
            "primary": ["python", "java", "go", "rust", "csharp", "sql", "api", "backend", "microservices", "docker"],
            "secondary": ["database", "mongodb", "postgresql", "redis", "elasticsearch", "gcp", "aws"],
            "avoid": ["react", "vue", "angular", "frontend", "css", "html", "ui/ux"]
        },
        "frontend": {
            "primary": ["javascript", "react", "vue", "angular", "typescript", "css", "frontend", "ui/ux"],
            "secondary": ["html", "webpack", "babel", "npm", "node.js"],
            "avoid": ["backend", "database", "devops", "infrastructure"]
        },
        "fullstack": {
            "primary": ["fullstack", "javascript", "python", "react", "api", "database", "node.js"],
            "secondary": ["docker", "aws", "gcp", "sql", "mongodb"],
            "avoid": []
        },
        "embedded": {
            "primary": ["c", "c++", "hardware", "iot", "embedded", "microcontroller", "firmware"],
            "secondary": ["rust", "assembly", "rtos", "fpga"],
            "avoid": ["python", "javascript", "react", "frontend", "backend"]
        },
        "devops": {
            "primary": ["docker", "kubernetes", "ci/cd", "devops", "aws", "azure", "gcp", "terraform", "ansible"],
            "secondary": ["python", "bash", "linux", "infrastructure", "monitoring"],
            "avoid": ["frontend", "ui/ux"]
        },
        "cybersecurity": {
            "primary": ["security", "cybersecurity", "pentesting", "infosec", "compliance", "ssl", "encryption"],
            "secondary": ["python", "bash", "network", "linux"],
            "avoid": ["ui/ux", "frontend design"]
        }
    }
    
    def __init__(self):
        self.mapping_cache = {}
        print_lg("[SKILL_MAPPER] Initialized with 6 resume types")
    
    def find_best_resume(self, job_skills: Dict[str, List[str]], 
                        available_resumes: List[str],
                        resume_type_skills: Optional[Dict[str, List[str]]] = None) -> Tuple[str, float]:
        """
        Find the best resume type for a job.
        
        Args:
            job_skills: Job requirements (from SkillExtractor)
            available_resumes: List of available resume types ["backend", "frontend", ...]
            resume_type_skills: Dict mapping resume types to skill lists (optional, for scoring)
        
        Returns:
            Tuple of (best_resume_type, match_score 0.0-1.0)
        """
        if not available_resumes:
            print_lg("[SKILL_MAPPER] No resumes available!")
            return None, 0.0
        
        best_match = None
        best_score = -1.0
        scores = {}
        
        # Get all job skills flattened and lowercased
        job_skills_flat = []
        for skill_list in job_skills.values():
            job_skills_flat.extend([s.lower() for s in skill_list])
        job_skills_flat = list(set(job_skills_flat))  # Remove duplicates
        
        print_lg(f"[SKILL_MAPPER] Analyzing {len(available_resumes)} resume types for {len(job_skills_flat)} job skills")
        
        # Score each available resume type
        for resume_type in available_resumes:
            score = self._score_resume_type(resume_type, job_skills_flat)
            scores[resume_type] = score
            
            if score > best_score:
                best_score = score
                best_match = resume_type
        
        # Log scores
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        ranking = ", ".join([f"{k}:{v:.2f}" for k, v in sorted_scores[:3]])
        print_lg(f"[SKILL_MAPPER] Top matches: {ranking}")
        
        return best_match, best_score
    
    def _score_resume_type(self, resume_type: str, job_skills: List[str]) -> float:
        """
        Score how well a resume type matches job skills.
        
        Scoring:
        - 1.0 for each primary skill match
        - 0.5 for each secondary skill match
        - -0.5 for each avoid skill match
        """
        if resume_type not in self.RESUME_TYPE_KEYWORDS:
            print_lg(f"[SKILL_MAPPER] Warning: Unknown resume type '{resume_type}'")
            return 0.0
        
        keywords = self.RESUME_TYPE_KEYWORDS[resume_type]
        score = 0.0
        max_score = len(keywords["primary"]) + len(keywords["secondary"])
        
        job_skills_lower = [s.lower() for s in job_skills]
        
        # Primary matches (worth 1.0 each)
        for primary in keywords["primary"]:
            for job_skill in job_skills_lower:
                if primary in job_skill or job_skill in primary:
                    score += 1.0
                    break
        
        # Secondary matches (worth 0.5 each)
        for secondary in keywords["secondary"]:
            for job_skill in job_skills_lower:
                if secondary in job_skill or job_skill in secondary:
                    score += 0.5
                    break
        
        # Avoid penalties (worth -0.5 each)
        for avoid in keywords.get("avoid", []):
            for job_skill in job_skills_lower:
                if avoid in job_skill or job_skill in avoid:
                    score -= 0.5
        
        # Normalize to 0.0-1.0 range
        if max_score > 0:
            normalized_score = max(0.0, min(1.0, score / max_score))
        else:
            normalized_score = 0.5
        
        return normalized_score
    
    def get_resume_type_for_skills(self, required_skills: List[str]) -> str:
        """
        Suggest a resume type based on required skills.
        
        Useful for matching existing resumes to jobs.
        """
        best_type = "fullstack"  # Default fallback
        best_score = -1.0
        
        for resume_type in self.RESUME_TYPE_KEYWORDS.keys():
            score = self._score_resume_type(resume_type, required_skills)
            if score > best_score:
                best_score = score
                best_type = resume_type
        
        return best_type
    
    def get_resume_hierarchy(self, job_skills: Dict[str, List[str]]) -> List[Tuple[str, float]]:
        """
        Get all resume types ranked by match quality.
        Useful for fallback logic.
        
        Returns:
            List of (resume_type, score) tuples, sorted by score descending
        """
        all_types = list(self.RESUME_TYPE_KEYWORDS.keys())
        
        # Get flattened job skills
        job_skills_flat = []
        for skill_list in job_skills.values():
            job_skills_flat.extend([s.lower() for s in skill_list])
        job_skills_flat = list(set(job_skills_flat))
        
        # Score all types
        scores = []
        for resume_type in all_types:
            score = self._score_resume_type(resume_type, job_skills_flat)
            scores.append((resume_type, score))
        
        # Sort by score descending
        return sorted(scores, key=lambda x: x[1], reverse=True)
