@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo CampusLoop's virtual environment was not found.
    echo Open README.md and follow the Quickstart setup instructions.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" "scripts\open_dashboard.py"
if errorlevel 1 pause 