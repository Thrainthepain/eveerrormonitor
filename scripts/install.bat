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
echo Testing installation...

REM Test virtual environment and dependencies
echo Checking virtual environment...
.venv\Scripts\python.exe --version
if errorlevel 1 (
    echo ERROR: Virtual environment Python not working
    goto :error
)

echo Testing required packages...
.venv\Scripts\python.exe -c "import psutil; print('✓ psutil available')"
if errorlevel 1 (
    echo ERROR: psutil package not working
    goto :error
)

.venv\Scripts\python.exe -c "import win32evtlog; print('✓ pywin32 available')"
if errorlevel 1 (
    echo ERROR: pywin32 package not working
    goto :error
)

echo Testing monitor script...
.venv\Scripts\python.exe python\test_installation.py
if errorlevel 1 (
    echo WARNING: Installation test failed
    goto :error
)

echo.
echo ✅ Installation completed successfully!
echo.
echo You can now run:
echo   scripts\run_monitor.bat          (Launch the crash monitor)
echo   E:\eve\.venv\Scripts\python.exe python\simple_eve_monitor.py   (Simple monitor)
echo.
goto :end

:error
echo.
echo ❌ Installation completed with errors.
echo The monitor may not work properly.
echo Try running this script as Administrator.
echo.

:end
pause
