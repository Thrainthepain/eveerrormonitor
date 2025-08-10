@echo off
echo Starting Eve Online Crash Monitor...
echo.
cd /d "%~dp0\..\python"
..\.venv\Scripts\python.exe eve_crash_monitor.py
pause
