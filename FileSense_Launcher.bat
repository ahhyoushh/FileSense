@echo off
cd /d "%~dp0"
call env\Scripts\activate.bat
if errorlevel 1 (
    echo [!] Failed to activate virtual environment!
    echo Please ensure 'env' exists and is a valid virtualenv.
    pause
    exit /b
)
echo Starting FileSense Launcher...
start "" pythonw scripts/launcher.py
exit
