"""
Resume Intelligence Module - Phase 2 Complete Implementation
Smart resume selection, skill extraction, and ATS optimization

Components:
- SkillExtractor: Extracts required skills from job descriptions (LLM + regex fallback)
- SkillMapper: Maps job skills to optimal resume type
- VariantGenerator: Creates 3-5 formatting variants per resume
- ATSTemplate: Ensures ATS compatibility and keyword optimization
- ResumeSelector: Orchestrates intelligent resume selection

Workflow:
1. Extract skills from job description
2. Map to best resume type based on skills
3. Select formatting variant (rotating for stealth)
4. Validate ATS compatibility
5. Log selection for analysis
"""

from .selector import ResumeSelector
from .skill_extractor import SkillExtractor
from .skill_mapper import SkillMapper
from .variant_generator import VariantGenerator
from .ats_templates import ATSTemplate

__all__ = [
    "ResumeSelector",
    "SkillExtractor",
    "SkillMapper",
    "VariantGenerator",
    "ATSTemplate"
]
