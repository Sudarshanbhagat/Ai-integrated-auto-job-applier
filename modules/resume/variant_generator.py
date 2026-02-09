"""
Resume Variant Generator - Creates formatting variants to avoid detection
Generates 3-5 different visual versions of the same resume content
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from modules.helpers import print_lg


class VariantGenerator:
    """
    Generates multiple visual variants of a resume.
    Same content, different formatting to avoid bot detection.
    
    Variants:
    - modern: Clean, colorful, contemporary
    - classic: Traditional, formal, safe
    - minimal: Minimal design, maximum whitespace
    - academic: Research-focused, publication-heavy
    - chronological: Timeline-focused, date-prominent
    """
    
    TEMPLATES = {
        "modern": {
            "colors": ["#0078D4", "#50E6FF", "#1D1D1D"],  # Blue, cyan, dark
            "fonts": ["Segoe UI", "Helvetica Neue"],
            "spacing": "1.5em",
            "borders": True,
            "description": "Contemporary design with accent colors"
        },
        "classic": {
            "colors": ["#000000", "#333333", "#FFFFFF"],  # Black, gray
            "fonts": ["Times New Roman", "Garamond"],
            "spacing": "1.2em",
            "borders": False,
            "description": "Traditional, formal presentation"
        },
        "minimal": {
            "colors": ["#1A1A1A", "#F5F5F5", "#555555"],  # Dark on light
            "fonts": ["Arial", "Helvetica"],
            "spacing": "0.9em",
            "borders": False,
            "description": "Minimal design with plenty of whitespace"
        },
        "academic": {
            "colors": ["#003366", "#333333", "#FFFFFF"],  # Navy, business
            "fonts": ["Calibri", "Cambria"],
            "spacing": "1.3em",
            "borders": False,
            "description": "Publication and research-focused layout"
        },
        "chronological": {
            "colors": ["#2E75B6", "#404040", "#FFFFFF"],  # Professional blue
            "fonts": ["Verdana", "Trebuchet MS"],
            "spacing": "1.4em",
            "borders": True,
            "description": "Timeline-focused with prominent dates"
        }
    }
    
    def __init__(self, variant_dir: str = "resumes/variants"):
        self.variant_dir = variant_dir
        self.created_variants: Dict[str, List[str]] = {}
        
        # Create variants directory if it doesn't exist
        os.makedirs(variant_dir, exist_ok=True)
        print_lg(f"[VARIANT_GEN] Initialized with {len(self.TEMPLATES)} templates")
    
    def generate_variants(self, resume_type: str, source_file: str, 
                         num_variants: int = 3) -> List[str]:
        """
        Generate variants of a resume.
        
        Args:
            resume_type: Type of resume (backend, frontend, fullstack, etc.)
            source_file: Path to source resume file
            num_variants: Number of variants to generate (3-5)
        
        Returns:
            List of variant file paths created
        """
        if num_variants < 1 or num_variants > 5:
            num_variants = 3
        
        if not os.path.exists(source_file):
            print_lg(f"[VARIANT_GEN] Source file not found: {source_file}")
            return []
        
        variants = []
        template_names = list(self.TEMPLATES.keys())
        
        # Select which templates to use
        selected_templates = template_names[:num_variants]
        
        for i, template_name in enumerate(selected_templates):
            variant_path = self._create_variant(
                resume_type=resume_type,
                source_file=source_file,
                template_name=template_name,
                variant_index=i
            )
            if variant_path and os.path.exists(variant_path):
                variants.append(variant_path)
        
        self.created_variants[resume_type] = variants
        print_lg(f"[VARIANT_GEN] Generated {len(variants)} variants for {resume_type}")
        return variants
    
    def _create_variant(self, resume_type: str, source_file: str,
                       template_name: str, variant_index: int) -> Optional[str]:
        """
        Create a single variant using a template.
        Currently creates metadata file (actual PDF generation would happen elsewhere)
        """
        try:
            # Create meaningful filename
            base_name = os.path.splitext(os.path.basename(source_file))[0]
            variant_name = f"{base_name}_{template_name}_v{variant_index + 1}"
            variant_path = os.path.join(self.variant_dir, f"{variant_name}.pdf")
            
            # Create metadata file
            metadata = {
                "source_file": source_file,
                "resume_type": resume_type,
                "template": template_name,
                "variant_index": variant_index,
                "variant_file": variant_path,
                "created_at": datetime.now().isoformat(),
                "template_config": self.TEMPLATES[template_name]
            }
            
            # Save metadata (for reference when applying)
            metadata_path = variant_path.replace(".pdf", ".json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            # Note: Actual PDF creation would happen here
            # For now, we just track the metadata
            print_lg(f"[VARIANT_GEN] Created variant: {template_name} ({variant_name})")
            
            return variant_path
            
        except Exception as e:
            print_lg(f"[VARIANT_GEN] Error creating variant: {e}")
            return None
    
    def get_next_variant(self, resume_type: str, last_used_template: Optional[str] = None) -> Optional[str]:
        """
        Get the next variant to use (rotating through them).
        
        Args:
            resume_type: Type of resume
            last_used_template: Which template was used last (to rotate)
        
        Returns:
            Path to next variant, or None if no variants exist
        """
        if resume_type not in self.created_variants:
            print_lg(f"[VARIANT_GEN] No variants found for {resume_type}")
            return None
        
        variants = self.created_variants[resume_type]
        if not variants:
            return None
        
        # If no last used template, return first
        if not last_used_template:
            return variants[0]
        
        # Find the position of the last used template
        for i, variant in enumerate(variants):
            if last_used_template in variant:
                # Return next variant (wrap around)
                next_index = (i + 1) % len(variants)
                return variants[next_index]
        
        # If not found, return first
        return variants[0]
    
    def rotate_variants(self, resume_type: str, current_index: int = 0) -> str:
        """
        Rotate through variants for load balancing.
        
        Args:
            resume_type: Type of resume
            current_index: Current variant index
        
        Returns:
            Path to next variant
        """
        if resume_type not in self.created_variants:
            return None
        
        variants = self.created_variants[resume_type]
        if not variants:
            return None
        
        next_index = (current_index + 1) % len(variants)
        return variants[next_index]
    
    def get_variant_info(self, variant_path: str) -> Optional[Dict]:
        """
        Get configuration info for a variant.
        
        Args:
            variant_path: Path to variant file
        
        Returns:
            Dict with template config, or None
        """
        metadata_path = variant_path.replace(".pdf", ".json")
        
        if not os.path.exists(metadata_path):
            return None
        
        try:
            with open(metadata_path, "r") as f:
                return json.load(f)
        except:
            return None
    
    def list_all_variants(self) -> Dict[str, List[str]]:
        """Get all created variants by resume type."""
        return self.created_variants.copy()
    
    def get_template_description(self, template_name: str) -> str:
        """Get human-readable description of a template."""
        if template_name in self.TEMPLATES:
            return self.TEMPLATES[template_name]["description"]
        return "Unknown template"
    
    def validate_variants(self, resume_type: str) -> bool:
        """
        Validate that all variants for a resume type exist.
        
        Returns:
            True if all variants exist and are accessible
        """
        if resume_type not in self.created_variants:
            return False
        
        for variant in self.created_variants[resume_type]:
            if not os.path.exists(variant):
                return False
        
        return True
