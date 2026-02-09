"""
ATS Templates - Provides ATS-safe resume formatting rules
Ensures resumes parse correctly through Applicant Tracking Systems
"""

from typing import Dict, List, Optional
from modules.helpers import print_lg


class ATSTemplate:
    """
    ATS-safe resume formatting templates.
    
    ATS Systems:
    - Workday
    - Greenhouse
    - iCIMS
    - Lever
    - SmartRecruiter
    - BrilliantHire
    """
    
    # Safe fonts that ATS systems can parse reliably
    SAFE_FONTS = [
        "Arial",
        "Times New Roman",
        "Calibri",
        "Verdana",
        "Courier New",
        "Garamond",
        "Cambria"
    ]
    
    # Fonts to AVOID (images, special characters)
    UNSAFE_FONTS = [
        "FontAwesome",
        "Wingdings",
        "Symbol",
        "Segoe UI Symbol",
        "DejaVu"
    ]
    
    # ATS-safe heading hierarchy
    HEADINGS = {
        "h1": "FULL NAME",  # Candidate name (uppercase)
        "h2": "PROFESSIONAL SUMMARY",  # Sections
        "h3": "Company Name",  # Company/Organization
    }
    
    # Sections to include (in order)
    SECTIONS = [
        "CONTACT INFORMATION",
        "PROFESSIONAL SUMMARY",
        "TECHNICAL SKILLS",
        "WORK EXPERIENCE",
        "EDUCATION",
        "CERTIFICATIONS",
        "PUBLICATIONS"
    ]
    
    def __init__(self):
        self.template_names = [
            "modern_ats",
            "classic_ats",
            "academic_ats"
        ]
        print_lg("[ATS_TEMPLATE] Initialized with 3 ATS-safe templates")
    
    def get_formatting_rules(self, template_name: str = "classic_ats") -> Dict:
        """
        Get ATS-safe formatting rules for a template.
        
        Returns:
            Dict with formatting rules and recommendations
        """
        if template_name not in self.template_names:
            template_name = "classic_ats"
        
        if template_name == "classic_ats":
            return {
                "font": "Times New Roman",
                "font_size": 11,
                "line_spacing": 1.15,
                "margins": {"top": 0.5, "bottom": 0.5, "left": 0.75, "right": 0.75},
                "colors": {"text": "000000", "section_header": "000000"},
                "use_images": False,
                "use_tables": False,  # Tables confuse some ATS
                "use_columns": False,  # Multi-column layouts break ATS
                "use_text_boxes": False,  # Text boxes don't parse well
                "header_style": "UPPERCASE",
                "date_format": "Month Year",  # e.g., "January 2023"
                "recommendations": [
                    "Use standard heading text, not images",
                    "Keep dates in Month Year format",
                    "Use bullet points for achievements",
                    "Avoid special characters and symbols",
                    "Use single column layout",
                    "Embed fonts to ensure rendering"
                ]
            }
        
        elif template_name == "modern_ats":
            return {
                "font": "Calibri",
                "font_size": 10,
                "line_spacing": 1.2,
                "margins": {"top": 0.5, "bottom": 0.5, "left": 0.75, "right": 0.75},
                "colors": {"text": "1a1a1a", "section_header": "003366"},
                "use_images": False,
                "use_tables": False,
                "use_columns": False,
                "use_text_boxes": False,
                "header_style": "Title Case",
                "date_format": "MM/YYYY",
                "recommendations": [
                    "Use horizontal lines between sections (not images)",
                    "Use simple, readable color scheme",
                    "Consistent spacing between sections",
                    "Use 0.5pt lines for visual separation",
                    "Keep technical skills in plain text lists"
                ]
            }
        
        elif template_name == "academic_ats":
            return {
                "font": "Cambria",
                "font_size": 11,
                "line_spacing": 1.25,
                "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1},
                "colors": {"text": "000000", "section_header": "003366"},
                "use_images": False,
                "use_tables": False,
                "use_columns": False,
                "use_text_boxes": False,
                "header_style": "Title Case",
                "date_format": "YYYY",  # For publications
                "recommendations": [
                    "Emphasize education and certifications",
                    "Include publication list with full citations",
                    "Use formal, academic language",
                    "Highlight research and presentations",
                    "Maintain consistent bibliography formatting"
                ]
            }
    
    def get_section_format(self, section_name: str) -> Dict:
        """
        Get ATS-safe formatting for a specific resume section.
        
        Returns:
            Dict with section-specific rules
        """
        section_formats = {
            "CONTACT INFORMATION": {
                "content": ["Name", "Email", "Phone", "LinkedIn URL", "City, State"],
                "format": "Plain text, one per line",
                "spacing": "1.0",
                "do": ["Use standard phone format (XXX) XXX-XXXX", "Use full URL for LinkedIn"],
                "dont": ["Use fancy formatting", "Use QR codes", "Use social media icons"]
            },
            "PROFESSIONAL SUMMARY": {
                "content": "2-3 sentence summary",
                "format": "Short paragraph",
                "spacing": "1.15",
                "do": ["Include key skills and years of experience", "Use relevant keywords"],
                "dont": ["Use bullet points", "Exceed 3 sentences", "Use first person pronouns"]
            },
            "TECHNICAL SKILLS": {
                "content": ["Programming Languages", "Frameworks", "Databases", "Tools"],
                "format": "Category: Item1, Item2, Item3",
                "spacing": "1.15",
                "do": ["Group skills by category", "List actual, relevant technologies"],
                "dont": ["Rate skills (Expert, Beginner)", "Use graphics or stars", "List irrelevant skills"]
            },
            "WORK EXPERIENCE": {
                "format": "Company Name | Job Title | Date Range",
                "description": "Bullet point achievements",
                "spacing": "1.15",
                "do": [
                    "Use clear job titles",
                    "Include month and year for dates",
                    "Start bullets with action verbs",
                    "Use metrics and results (achieved X, improved Y%)"
                ],
                "dont": [
                    "Use special characters in job titles",
                    "Use only years (include months)",
                    "Use graphics or icons",
                    "List tasks instead of achievements"
                ]
            },
            "EDUCATION": {
                "format": "Degree | Institution | Date",
                "spacing": "1.15",
                "do": [
                    "Include GPA if 3.5 or higher",
                    "List relevant coursework",
                    "Include graduation date"
                ],
                "dont": [
                    "Use special formatting",
                    "Include unfinished degrees",
                    "Use graphics"
                ]
            },
            "CERTIFICATIONS": {
                "format": "Certification Name | Issuing Body | Date",
                "spacing": "1.15",
                "do": [
                    "Use full certification names",
                    "Include issuing organization",
                    "Include expiration date if applicable"
                ],
                "dont": [
                    "Use logos",
                    "Use informal names",
                    "Include expired certifications"
                ]
            }
        }
        
        return section_formats.get(section_name, {})
    
    def validate_resume_content(self, resume_content: Dict) -> List[str]:
        """
        Validate resume content for ATS compatibility.
        
        Returns:
            List of warnings/issues found
        """
        warnings = []
        
        # Check for unsafe fonts
        if "font" in resume_content and resume_content["font"] in self.UNSAFE_FONTS:
            warnings.append(f"WARNING: Unsafe font detected: {resume_content['font']}")
        
        # Check for multi-column layout
        if resume_content.get("use_columns"):
            warnings.append("WARNING: Multi-column layout detected (bad for ATS)")
        
        # Check for images/graphics
        if resume_content.get("has_images"):
            warnings.append("WARNING: Resume contains images/graphics (ATS may not parse)")
        
        # Check for tables
        if resume_content.get("has_tables"):
            warnings.append("WARNING: Resume uses tables (some ATS systems struggle with this)")
        
        # Check for text boxes
        if resume_content.get("has_text_boxes"):
            warnings.append("WARNING: Text boxes detected (may not parse in ATS)")
        
        # Check dates format
        if "date_format" in resume_content and resume_content["date_format"] not in ["Month Year", "MM/YYYY", "YYYY"]:
            warnings.append(f"WARNING: Non-standard date format: {resume_content['date_format']}")
        
        return warnings
    
    def get_keyword_optimization_tips(self, keywords: List[str]) -> Dict:
        """
        Tips for optimizing resume keywords for ATS.
        
        Args:
            keywords: List of required keywords from job description
        
        Returns:
            Dict with optimization recommendations
        """
        return {
            "total_keywords": len(keywords),
            "keywords_to_include": keywords,
            "placement_suggestions": {
                "professional_summary": "Include 2-3 most important keywords",
                "technical_skills": "Include 5-10 relevant technical keywords",
                "work_experience": "Naturally work in keywords in achievement bullets",
                "education": "Include relevant coursework keywords if applicable"
            },
            "optimization_tips": [
                f"Include '{keywords[0]}' early in professional summary" if keywords else "",
                "Use exact terminology from job description",
                "Include keywords in context (not forced lists)",
                "Match job description terminology exactly",
                "Avoid acronyms without explanation (spell out first use)"
            ],
            "distribute_keywords": True,
            "avoid_overuse": "Don't repeat keywords more than 5-10 times total"
        }
    
    def get_ats_compatibility_score(self, resume_metadata: Dict) -> float:
        """
        Score how ATS-compatible a resume is (0.0-1.0).
        
        Args:
            resume_metadata: Dict with resume properties
        
        Returns:
            Score from 0.0 (not safe) to 1.0 (fully compatible)
        """
        score = 1.0
        
        # Check font safety
        if resume_metadata.get("font") not in self.SAFE_FONTS:
            score -= 0.1
        
        # Check for problematic elements
        if resume_metadata.get("has_images"):
            score -= 0.2
        if resume_metadata.get("has_tables"):
            score -= 0.15
        if resume_metadata.get("has_text_boxes"):
            score -= 0.15
        if resume_metadata.get("use_columns"):
            score -= 0.15
        
        # Check for proper structure
        if not resume_metadata.get("has_clear_sections"):
            score -= 0.1
        
        # Ensure minimum compatibility
        return max(0.0, min(1.0, score))
