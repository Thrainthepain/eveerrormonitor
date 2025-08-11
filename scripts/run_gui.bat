@echo off
echo Starting Eve Online Crash Monitor GUI...
echo.

cd /d "%~dp0"
cd ..\python

REM Check if virtual environment exists
if not exist "..\\.venv\\Scripts\\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first to install dependencies.
    pause
    exit /b 1
)

REM Run the GUI
"..\\.venv\\Scripts\\python.exe" crash_monitor_gui.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start the GUI.
    echo Make sure all dependencies are installed correctly.
    pause
)
