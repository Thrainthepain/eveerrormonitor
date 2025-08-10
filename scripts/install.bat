@echo off
echo Installing Eve Online Crash Monitor...
echo.

cd /d "%~dp0\.."

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Creating virtual environment...

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    python -m venv .venv
)

echo Activating virtual environment and installing dependencies...

REM Activate virtual environment and install dependencies
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r python\requirements.txt

if errorlevel 1 (
    echo.
    echo WARNING: Failed to install some dependencies.
    echo The monitor may not work with full functionality.
    echo.
)

echo.
echo Installation complete!
echo.
echo You can now run:
echo   scripts\run_monitor.bat          (Launch the crash monitor)
echo   python simple_eve_monitor.py   (Simple monitor with basic features)
echo.
pause
