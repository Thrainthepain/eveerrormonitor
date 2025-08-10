@echo off
echo Starting Eve Online Crash Monitor...
echo.

REM Change to project root directory
cd /d "%~dp0\.."

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please run scripts\install.bat first
    pause
    exit /b 1
)

REM Check if monitor script exists
if not exist "python\eve_crash_monitor.py" (
    echo ERROR: Monitor script not found at python\eve_crash_monitor.py
    pause
    exit /b 1
)

echo Launching monitor from: %CD%
echo Using Python: .venv\Scripts\python.exe
echo Monitor script: python\eve_crash_monitor.py
echo.

REM Run the monitor from project root, specifying the python script path
.venv\Scripts\python.exe python\eve_crash_monitor.py

echo.
echo Monitor has exited.
pause
