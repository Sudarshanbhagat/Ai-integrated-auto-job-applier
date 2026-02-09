import os
import time
import subprocess

from config.settings import (
    run_in_background,
    stealth_mode,
    disable_extensions,
    safe_mode,
    file_name,
    failed_file_name,
    logs_folder_path,
    generated_resume_path,
    chrome_version_main,
    chrome_use_subprocess,
    chrome_kill_existing,
    chrome_profile_path
)

from config.questions import default_resume_path
from modules.helpers import make_directories, find_default_profile_directory, print_lg

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import SessionNotCreatedException

# Selenium / UC imports
if stealth_mode:
    import undetected_chromedriver as uc
else:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options


# =====================================================
# SAFE PROFILE DIRECTORY (NO TEMP, NO GUEST)
# =====================================================

PROFILE_BASE = chrome_profile_path or os.path.join(
    os.getenv("LOCALAPPDATA"),
    "AutoJobBot",
    "Profile"
)

os.makedirs(PROFILE_BASE, exist_ok=True)


# =====================================================
# MAIN CHROME SESSION CREATOR
# =====================================================

def createChromeSession(isRetry: bool = False):

    # Ensure project directories exist
    make_directories([
        file_name,
        failed_file_name,
        logs_folder_path + "/screenshots",
        default_resume_path,
        generated_resume_path + "/temp"
    ])

    print_lg("Starting Chrome session...")
    print_lg(f"Using profile directory: {PROFILE_BASE}")

    # Base arguments
    base_args = []

    if run_in_background:
        base_args.append("--headless=new")

    if disable_extensions:
        base_args.append("--disable-extensions")

    base_args.extend([
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-notifications"
    ])

    # Kill old Chrome if enabled
    if chrome_kill_existing:
        try:
            print_lg("Killing existing Chrome processes...")
            for name in ("chrome.exe", "chromedriver.exe"):
                subprocess.run(
                    ["taskkill", "/F", "/IM", name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            time.sleep(2)
        except Exception:
            print_lg("Warning: Could not kill Chrome processes")

    # =================================================
    # STEALTH MODE (Undetected Chrome)
    # =================================================
    if stealth_mode:

        print_lg("Launching Undetected ChromeDriver...")

        last_error = None

        for attempt, delay in enumerate((0, 5, 15), start=1):

            try:
                print_lg(f"Chrome launch attempt {attempt}")

                # Fresh options per attempt
                options = uc.ChromeOptions()

                for arg in base_args:
                    options.add_argument(arg)

                # FORCE SAFE PROFILE (NO TEMP)
                options.add_argument(f"--user-data-dir={PROFILE_BASE}")

                driver = uc.Chrome(
                    options=options,
                    version_main=chrome_version_main,
                    use_subprocess=chrome_use_subprocess
                )

                break  # Success

            except SessionNotCreatedException as e:

                last_error = e
                print_lg(f"Session error on attempt {attempt}: {e}")

                if attempt < 3:
                    print_lg(f"Retrying after {delay}s...")
                    time.sleep(delay)
                else:
                    raise

            except Exception as e:

                last_error = e
                print_lg(f"Chrome failed on attempt {attempt}: {e}")

                if attempt < 3:
                    time.sleep(delay)
                else:
                    raise

    # =================================================
    # NORMAL SELENIUM MODE (Fallback)
    # =================================================
    else:

        print_lg("Launching normal Selenium Chrome...")

        options = Options()

        for arg in base_args:
            options.add_argument(arg)

        options.add_argument(f"--user-data-dir={PROFILE_BASE}")

        driver = webdriver.Chrome(options=options)

    # =================================================
    # POST-INIT
    # =================================================

    driver.maximize_window()

    try:
        caps = driver.capabilities
        browser_version = caps.get("browserVersion") or caps.get("version")

        print_lg(f"[BROWSER] Chrome Version: {browser_version}")

    except Exception:
        pass

    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    print_lg("Chrome session created successfully.")

    return options, driver, actions, wait
