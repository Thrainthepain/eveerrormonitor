@echo off
echo Starting Eve Online Crash Monitor (Interactive Mode)...
echo.

cd /d "%~dp0"
cd ..\python

REM Check if virtual environment exists
if not exist "..\\.venv\\Scripts\\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run scripts\install.bat first to install dependencies.
    pause
    exit /b 1
)

REM Run the interactive monitor
echo Running crash monitor in interactive command mode...
echo You will be able to use commands like 'start', 'stop', 'status', 'quit'
echo.
"..\\.venv\\Scripts\\python.exe" eve_crash_monitor.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start the crash monitor.
    echo Make sure all dependencies are installed correctly.
    pause
)
