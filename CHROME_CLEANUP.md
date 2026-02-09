Chrome & Undetected-Chromedriver Cleanup

If you encounter startup errors (SessionNotCreated or port/connection errors), follow these steps:

1. Close all Chrome windows.
2. Kill lingering processes (Windows PowerShell):

```powershell
taskkill /F /IM chromedriver.exe
taskkill /F /IM chrome.exe
```

3. Remove undetected_chromedriver cache folder (it will be re-downloaded):

Path (Windows):
`%APPDATA%\undetected_chromedriver\undetected`

4. Clear temporary profile folder used by the tool (if present):

```powershell
Remove-Item -Recurse -Force .\temp_profile_folder_path
```

5. Restart the application.

Optional: If Chrome has recently auto-updated, set `chrome_version_main` in `config/settings.py` to match the major version shown in `chrome://version`.

Verification commands:

```powershell
# Check Chrome version
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version

# Check for running processes
tasklist | findstr chrome
```

If issues persist, enable `safe_mode = True` in `config/settings.py` to force a guest profile launch, or consult the project README and Discord support.