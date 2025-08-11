@echo off
echo ===============================================
echo Eve Online Crash Monitor - Setup Script
echo ===============================================
echo.

cd /d "%~dp0"
cd ..

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [2/3] Creating configuration directory...
if not exist "config" mkdir config

echo [3/3] Creating logs directory...
if not exist "logs" mkdir logs

echo.
echo ===============================================
echo Setup completed successfully!
echo ===============================================
echo.
echo Next steps:
echo   1. Run 'scripts\install.bat' to install dependencies
echo   2. Run 'scripts\run_gui.bat' to start the GUI
echo.
pause