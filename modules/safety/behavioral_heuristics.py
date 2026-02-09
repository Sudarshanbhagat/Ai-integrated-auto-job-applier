"""
Behavioral Heuristics Module - Simulates human-like behavior patterns
Adds randomness, pauses, typos, and realistic interactions to avoid detection
"""

import random
import time as time_module
from typing import List, Optional
from modules.helpers import print_lg, sleep
from .constants import BEHAVIOR_CONFIG


class BehavioralHeuristics:
    """
    Injection of human-like behaviors:
    - Random pauses and interruptions
    - Realistic mouse movements
    - Variable scroll speeds
    - Typing with typos and variable speed
    - Pre-apply research (reading job descriptions)
    - Occasionally skipping or saving good jobs
    - Saving jobs instead of applying (reduces applies per day count)
    """
    
    def __init__(self):
        self.config = BEHAVIOR_CONFIG
        self.typing_mistakes = []
        self.jobs_researched = 0
        self.jobs_saved = 0
        self.jobs_skipped = 0
        
    def should_take_random_break(self) -> bool:
        """
        Randomly decide if we should take a break now.
        ~8% chance per call.
        """
        probability = self.config.get("random_interruption_probability", 0.08)
        return random.random() < probability
    
    def take_random_pause(self):
        """Take a random pause (30 sec to 3 min) as if distracted"""
        min_sec = self.config["random_pause_duration_sec"][0]
        max_sec = self.config["random_pause_duration_sec"][1]
        pause_duration = random.randint(min_sec, max_sec)
        
        reason = random.choice([
            "checking email",
            "reading news",
            "taking a sip of coffee",
            "answering a message",
            "thinking about the job",
        ])
        
        print_lg(f"[BEHAVIOR] Random pause ({reason}): {pause_duration}s")
        sleep(pause_duration)
    
    def should_save_job_instead_of_apply(self) -> bool:
        """
        Decide if we should save job for later instead of applying.
        ~15% of jobs should be saved.
        """
        probability = self.config.get("save_jobs_probability", 0.15)
        if random.random() < probability:
            print_lg("[BEHAVIOR] Saving job for later instead of applying")
            self.jobs_saved += 1
            return True
        return False
    
    def should_skip_good_job(self) -> bool:
        """
        Occasionally skip a suitable job to seem non-robotic.
        ~5% chance.
        """
        probability = self.config.get("skip_good_job_probability", 0.05)
        if random.random() < probability:
            print_lg("[BEHAVIOR] Skipping suitable job (human-like behavior)")
            self.jobs_skipped += 1
            return True
        return False
    
    def research_job_before_applying(self, driver) -> bool:
        """
        Simulate reading/researching the job before applying.
        Scroll through job description, read requirements, etc.
        
        Args:
            driver: Selenium WebDriver
            
        Returns:
            True if research completed
        """
        if not self.config.get("pre_apply_research", True):
            return True
        
        try:
            # Simulate reading time
            read_duration = random.uniform(5, 20)  # 5-20 seconds
            print_lg(f"[BEHAVIOR] Researching job ({read_duration:.0f}s)...")
            
            # Random scrolling to appear to be reading
            for _ in range(random.randint(2, 5)):
                scroll_amount = random.randint(100, 500)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                sleep(random.uniform(1, 3))
            
            # Scroll back to top
            driver.execute_script("window.scrollTo(0, 0);")
            sleep(random.uniform(0.5, 1.5))
            
            self.jobs_researched += 1
            return True
        except Exception as e:
            print_lg(f"[BEHAVIOR] Warning: Failed to research job: {e}")
            return False
    
    def type_with_human_speed(self, element, text: str):
        """
        Type text at human speed with occasional typos.
        Uses realistic typing speed (40-80 WPM).
        
        Args:
            element: Selenium WebElement to type into
            text: Text to type
        """
        if not self.config.get("slow_typing_enabled", True):
            # Just send keys normally
            element.send_keys(text)
            return
        
        wpm_range = self.config.get("typing_speed_wpm", (40, 80))
        wpm = random.uniform(wpm_range[0], wpm_range[1])
        
        # WPM = characters per minute / 5
        avg_chars_per_second = (wpm * 5) / 60
        delay_per_char = 1.0 / avg_chars_per_second
        
        # Randomly inject typos (~2% chance)
        typo_probability = self.config.get("typo_probability", 0.02)
        text_with_typos = self._inject_typos(text, typo_probability)
        
        print_lg(f"[BEHAVIOR] Typing at {wpm:.0f} WPM...")
        
        for char in text_with_typos:
            element.send_keys(char)
            # Add some variance to timing
            variance = random.gauss(0, delay_per_char * 0.3)
            sleep(max(0.05, delay_per_char + variance))  # Min 50ms
    
    def _inject_typos(self, text: str, typo_probability: float) -> str:
        """Randomly introduce typos and corrections"""
        if random.random() > typo_probability:
            return text
        
        # Find random position
        if len(text) < 2:
            return text
        
        pos = random.randint(1, len(text) - 1)
        char_to_replace = text[pos]
        
        # Create typo by pressing wrong key
        typo_chars = random.choice("qwertyuiopasdfghjklzxcvbnm")
        
        # Return text with typo + deletion + correction
        result = text[:pos] + typo_chars + text[pos:]
        result += "\b"  # Simulated backspace
        result += char_to_replace
        
        return result
    
    def human_like_variable_scroll(self, driver, target_element=None, scroll_range: tuple = (100, 500)):
        """
        Scroll smoothly with variable speeds like a human would.
        
        Args:
            driver: Selenium WebDriver
            target_element: Optional element to scroll to
            scroll_range: Tuple of (min_pixels, max_pixels) to scroll
        """
        if not self.config.get("variable_scroll_speed", True):
            # Just use default scroll
            if target_element:
                driver.execute_script("arguments[0].scrollIntoView();", target_element)
            return
        
        try:
            if target_element:
                # Scroll to element with variable speed
                target_location = target_element.location['y']
                current_position = driver.execute_script("return window.pageYOffset;")
                distance = target_location - current_position - 200  # Leave some buffer
            else:
                distance = random.randint(scroll_range[0], scroll_range[1])
            
            # Variable scroll speed (pixels per step)
            scroll_speed = random.uniform(50, 200)
            num_steps = max(2, int(abs(distance) / scroll_speed))
            
            for i in range(num_steps):
                step_distance = distance / num_steps
                sleep(random.uniform(0.05, 0.2))  # Brief pause between scrolls
                driver.execute_script(f"window.scrollBy(0, {step_distance});")
        except Exception as e:
            print_lg(f"[BEHAVIOR] Warning: Failed to scroll: {e}")
    
    def simulate_mouse_movement(self, driver, target_x: int, target_y: int) -> bool:
        """
        Simulate realistic mouse movement to target coordinates.
        Uses curved path, variable speed.
        
        Args:
            driver: Selenium WebDriver
            target_x: Target X coordinate
            target_y: Target Y coordinate
            
        Returns:
            True if successful
        """
        if not self.config.get("human_mouse_movement", True):
            return True
        
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            # Get current mouse position (approximate)
            current_x = 0
            current_y = 0
            
            # Calculate distance
            distance = ((target_x - current_x)**2 + (target_y - current_y)**2)**0.5
            
            # Number of steps in path
            num_steps = max(10, int(distance / 50))
            
            actions = ActionChains(driver)
            for i in range(num_steps):
                # Ease-in curve for more natural movement
                progress = i / num_steps
                ease_progress = progress * progress  # Quadratic easing
                
                intermediate_x = current_x + (target_x - current_x) * ease_progress
                intermediate_y = current_y + (target_y - current_y) * ease_progress
                
                actions.move_by_offset(
                    intermediate_x - (current_x + (target_x - current_x) * ((i-1) / num_steps)**2) if i > 0 else 0,
                    intermediate_y - (current_y + (target_y - current_y) * ((i-1) / num_steps)**2) if i > 0 else 0
                )
                sleep(random.uniform(0.02, 0.1))
            
            actions.perform()
            return True
        except Exception as e:
            print_lg(f"[BEHAVIOR] Warning: Mouse movement simulation failed: {e}")
            return False
    
    def get_behavior_stats(self) -> dict:
        """Return statistics about behaviors performed"""
        return {
            "jobs_researched": self.jobs_researched,
            "jobs_saved": self.jobs_saved,
            "jobs_skipped_intentionally": self.jobs_skipped,
            "typing_typos_injected": len(self.typing_mistakes),
        }
