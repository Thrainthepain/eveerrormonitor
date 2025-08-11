@echo off
echo ===============================================
echo Eve Online Crash Monitor - Installation Script
echo ===============================================
echo.

cd /d "%~dp0"
cd ..

echo [1/4] Creating Python virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment!
    echo Please ensure Python 3.8+ is installed and accessible.
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/4] Installing required packages...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r python\requirements.txt
if errorlevel 1 (
    echo Error: Failed to install required packages!
    pause
    exit /b 1
)

echo [4/4] Creating logs directory...
if not exist "logs" mkdir logs

echo.
echo ===============================================
echo Installation completed successfully!
echo ===============================================
echo.
echo You can now run:
echo   - scripts\run_gui.bat (to start the GUI)
echo   - scripts\run_monitor.bat (to run command-line monitor)
echo.
pause