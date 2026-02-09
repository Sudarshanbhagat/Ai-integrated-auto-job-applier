"""
Skill Extractor - Extracts required skills from job descriptions
Uses LLM if available, falls back to regex pattern matching
"""

import json
import re
from typing import Dict, List, Optional
from modules.helpers import print_lg


class SkillExtractor:
    """
    Extracts and categorizes skills from job descriptions.
    
    Supports:
    - LLM-based extraction (OpenAI, DeepSeek, Gemini)
    - Regex fallback for when LLM unavailable
    - Categorization: Tech Stack, Technical Skills, Other Skills, Required, Nice-to-Have
    """
    
    # Common skill patterns for regex fallback
    TECH_STACK_PATTERNS = {
        "python": r"\bpython\b",
        "javascript": r"\b(javascript|js|node\.js|nodejs)\b",
        "java": r"\bjava\b",
        "csharp": r"\bc#|\.net\b",
        "golang": r"\bgo\b|\bgolang\b",
        "rust": r"\brust\b",
        "typescript": r"\btypescript\b",
        "react": r"\breact\b|\breact\.js\b",
        "vue": r"\bvue\b|\bvue\.js\b",
        "angular": r"\bangular\b",
        "pytorch": r"\bpytorch\b",
        "tensorflow": r"\btensorflow\b",
        "aws": r"\baws\b|\bamazon web services\b",
        "gcp": r"\bgcp\b|\bgoogle cloud\b",
        "azure": r"\bazure\b|\bmicrosoft azure\b",
        "docker": r"\bdocker\b",
        "kubernetes": r"\bkubernetes\b|\bk8s\b",
        "sql": r"\bsql\b|\bmysql\b|\bpostgres\b|\bpostgresql\b",
        "mongodb": r"\bmongodb\b",
        "redis": r"\bredis\b",
        "elasticsearch": r"\belasticsearch\b",
        "graphql": r"\bgraphql\b",
        "rest": r"\brest api\b|\brest\b",
    }
    
    SOFT_SKILLS_PATTERNS = {
        "communication": r"\bcommunication\b",
        "leadership": r"\bleadership\b",
        "teamwork": r"\bteam\b|\bcollaboration\b",
        "problem_solving": r"\bproblem.solving\b",
        "time_management": r"\btime.management\b",
        "adaptability": r"\badaptability\b|\badapt\b",
    }
    
    def __init__(self, use_llm: bool = False, llm_client=None):
        self.use_llm = use_llm
        self.llm_client = llm_client
        self.extraction_method = "llm" if (use_llm and llm_client) else "regex"
        print_lg(f"[SKILLS] Extractor initialized - Method: {self.extraction_method}")
    
    def extract(self, job_description: str, job_title: str = "", company: str = "") -> Dict[str, List[str]]:
        """
        Extract skills from job description.
        
        Args:
            job_description: Full job description text
            job_title: Job title (for context)
            company: Company name (for context)
        
        Returns:
            Dictionary with skill categories:
            {
                "tech_stack": [...],
                "technical_skills": [...],
                "soft_skills": [...],
                "required": [...],
                "nice_to_have": [...]
            }
        """
        if self.use_llm and self.llm_client:
            return self._extract_with_llm(job_description, job_title, company)
        else:
            return self._extract_with_regex(job_description)
    
    def _extract_with_llm(self, job_description: str, job_title: str, company: str) -> Dict[str, List[str]]:
        """Extract skills using LLM"""
        try:
            from config.secrets import ai_provider
            from modules.ai.prompts import extract_skills_prompt
            
            # Prepare prompt
            context = f"Job Title: {job_title}\nCompany: {company}\n\n{job_description}"
            prompt = extract_skills_prompt.format(context)
            
            # Get LLM response
            if ai_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=500
                )
                content = response.choices[0].message.content
            elif ai_provider == "deepseek":
                response = self.llm_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=500
                )
                content = response.choices[0].message.content
            else:
                content = ""
            
            # Parse JSON response
            try:
                skills = json.loads(content)
                print_lg(f"[SKILLS] LLM extraction successful - {len(skills.get('tech_stack', []))} tech skills found")
                return skills
            except json.JSONDecodeError:
                print_lg("[SKILLS] LLM response was not valid JSON, falling back to regex")
                return self._extract_with_regex(job_description)
        
        except Exception as e:
            print_lg(f"[SKILLS] LLM extraction failed: {e}, falling back to regex")
            return self._extract_with_regex(job_description)
    
    def _extract_with_regex(self, job_description: str) -> Dict[str, List[str]]:
        """Extract skills using regex patterns"""
        description_lower = job_description.lower()
        
        # Extract tech stack
        tech_stack = []
        for skill, pattern in self.TECH_STACK_PATTERNS.items():
            if re.search(pattern, description_lower):
                tech_stack.append(skill.replace("_", " ").title())
        
        # Extract soft skills
        soft_skills = []
        for skill, pattern in self.SOFT_SKILLS_PATTERNS.items():
            if re.search(pattern, description_lower):
                soft_skills.append(skill.replace("_", " ").title())
        
        # Extract "required" vs "nice-to-have"
        required = []
        nice_to_have = []
        
        # Skills after "required" keyword
        required_section = re.search(r"(must have|required|essential)(.*?)(?=nice|preferred|optional|$)", 
                                     description_lower, re.DOTALL)
        if required_section:
            required_text = required_section.group(2)
            for skill, pattern in self.TECH_STACK_PATTERNS.items():
                if re.search(pattern, required_text):
                    required.append(skill.replace("_", " ").title())
        
        # Skills after "nice-to-have" keyword
        nice_section = re.search(r"(nice.to.have|preferred|optional)(.*?)(?=$|experience)", 
                                description_lower, re.DOTALL)
        if nice_section:
            nice_text = nice_section.group(2)
            for skill, pattern in self.TECH_STACK_PATTERNS.items():
                if re.search(pattern, nice_text):
                    nice_to_have.append(skill.replace("_", " ").title())
        
        # Remove duplicates and sort
        tech_stack = sorted(list(set(tech_stack)))
        soft_skills = sorted(list(set(soft_skills)))
        required = sorted(list(set(required)))
        nice_to_have = sorted(list(set(nice_to_have)))
        
        return {
            "tech_stack": tech_stack,
            "technical_skills": ["System Design", "API Design", "Database Design"],  # Common ones
            "soft_skills": soft_skills,
            "required": required if required else tech_stack[:3],  # Fallback to top 3
            "nice_to_have": nice_to_have
        }
    
    def score_match(self, job_skills: Dict[str, List[str]], resume_skills: List[str]) -> float:
        """
        Score how well resume skills match job requirements.
        
        Args:
            job_skills: Extracted job skills
            resume_skills: Skills listed on this resume
        
        Returns:
            Score from 0.0 to 1.0 (1.0 = perfect match)
        """
        resume_skills_lower = [s.lower() for s in resume_skills]
        
        # Check required skills
        required = [s.lower() for s in job_skills.get("required", [])]
        matched_required = sum(1 for s in required if any(r in s for r in resume_skills_lower))
        required_score = matched_required / len(required) if required else 0.5
        
        # Check tech stack
        tech_stack = [s.lower() for s in job_skills.get("tech_stack", [])]
        matched_tech = sum(1 for s in tech_stack if any(t in s for t in resume_skills_lower))
        tech_score = matched_tech / len(tech_stack) if tech_stack else 0.5
        
        # Combined score (required weighted higher)
        overall_score = (required_score * 0.6) + (tech_score * 0.4)
        return min(1.0, max(0.0, overall_score))
