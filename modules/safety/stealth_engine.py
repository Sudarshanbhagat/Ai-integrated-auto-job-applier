"""
Stealth Engine Module - Anti-detection and fingerprint spoofing
Masks automation indicators and simulates legitimate browser behavior
"""

import random
from typing import List, Dict
from modules.helpers import print_lg
from .constants import STEALTH_CONFIG


class StealthEngine:
    """
    Comprehensive stealth layer that:
    - Removes navigator.webdriver flag
    - Patches ChromeDriver detection strings
    - Injects JS to defeat fingerprinting
    - Rotates user agents
    - Adds canvas noise
    - Matches system timezone/language
    - Varies screen resolution
    """
    
    # High-quality desktop user agents (not mobile)
    DESKTOP_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]
    
    # Common screen resolutions
    SCREEN_RESOLUTIONS = [
        (1920, 1080),
        (1366, 768),
        (1440, 900),
        (1536, 864),
        (1680, 1050),
        (1920, 1200),
        (2560, 1440),
    ]
    
    # Stealth JS injections
    STEALTH_JS_SCRIPTS = [
        # Hide navigator.webdriver
        """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        """,
        
        # Remove headless indicators
        """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        """,
        
        # Patch chrome property
        """
        window.chrome = {
            runtime: {}
        };
        """,
        
        # Add canvas noise for fingerprinting evasion
        """
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {
            if (type === 'image/png' || type === 'image/jpeg') {
                const context = this.getContext('2d');
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] += Math.floor(Math.random() * 10);
                    imageData.data[i + 1] += Math.floor(Math.random() * 10);
                    imageData.data[i + 2] += Math.floor(Math.random() * 10);
                }
                context.putImageData(imageData, 0, 0);
            }
            return originalToDataURL.call(this, type);
        };
        """,
        
        # Mask puppeteer/playwright presence
        """
        delete Object.getPrototypeOf(navigator).permissions;
        """,
    ]
    
    def __init__(self):
        self.config = STEALTH_CONFIG
        self.current_user_agent = None
        self.current_screen_resolution = None
        
    def get_chrome_options(self) -> List[str]:
        """
        Return Chrome arguments for stealth mode.
        Add these to ChromeOptions when creating the driver.
        """
        options = []
        
        if not self.config["headless_mode"]:
            # Don't use headless - it's too detectable
            pass
        
        # Disable known automation indicators
        for feature in self.config.get("disable_blink_features", []):
            options.append(f"--disable-blink-features={feature}")
        
        # Disable dev tools protocol
        options.append("--disable-dev-shm-usage")
        
        # Randomize other flags to look legitimate
        if random.random() > 0.5:
            options.append("--disable-extensions")
        
        if random.random() > 0.3:
            options.append("--disable-sync")
        
        return options
    
    def get_random_user_agent(self) -> str:
        """
        Get a random, high-quality desktop user agent.
        Desktop-only to avoid mobile-specific limitations.
        """
        self.current_user_agent = random.choice(self.DESKTOP_USER_AGENTS)
        print_lg(f"[STEALTH] Using user agent: {self.current_user_agent[:80]}...")
        return self.current_user_agent
    
    def get_random_screen_resolution(self) -> tuple:
        """Get a random but realistic screen resolution"""
        self.current_screen_resolution = random.choice(self.SCREEN_RESOLUTIONS)
        print_lg(f"[STEALTH] Using screen resolution: {self.current_screen_resolution[0]}x{self.current_screen_resolution[1]}")
        return self.current_screen_resolution
    
    def inject_stealth_scripts(self, driver) -> bool:
        """
        Inject stealth JavaScript into page to defeat fingerprinting.
        Should be called after driver is created but before navigating.
        
        Returns:
            True if successful, False if injection failed
        """
        if not self.config["js_fingerprint_patch"]:
            return True
        
        try:
            for i, script in enumerate(self.STEALTH_JS_SCRIPTS):
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    "source": script
                })
            print_lg(f"[STEALTH] Injected {len(self.STEALTH_JS_SCRIPTS)} stealth scripts")
            return True
        except Exception as e:
            print_lg(f"[STEALTH] Warning: Failed to inject stealth scripts: {e}")
            # Don't fail - undetected-chromedriver may handle this differently
            return False
    
    def get_stealth_headers(self) -> Dict[str, str]:
        """
        Return HTTP headers that appear more legitimate.
        Use these with requests library if making direct HTTP calls.
        """
        return {
            "User-Agent": self.current_user_agent or self.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    def configure_chrome_options(self, options) -> None:
        """
        Configure Chrome options for maximum stealth.
        Modifies options object in-place.
        
        Args:
            options: selenium.webdriver.chrome.options.Options or uc.ChromeOptions
        """
        # Add user agent
        user_agent = self.get_random_user_agent()
        options.add_argument(f"user-agent={user_agent}")
        
        # Add stealth arguments
        for arg in self.get_chrome_options():
            options.add_argument(arg)
        
        # Disable some common detection vectors
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_settings.popups": 0,
        }
        options.add_experimental_option("prefs", prefs)
        
        print_lg("[STEALTH] Chrome options configured for stealth mode")
    
    def get_config_summary(self) -> Dict:
        """Return current stealth configuration"""
        return {
            "hide_navigator_webdriver": self.config["hide_navigator_webdriver"],
            "js_fingerprint_patch": self.config["js_fingerprint_patch"],
            "canvas_noise": self.config["canvas_noise"],
            "user_agent": self.current_user_agent or "Not set yet",
            "screen_resolution": str(self.current_screen_resolution) if self.current_screen_resolution else "Not set yet",
        }
