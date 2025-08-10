@echo off
echo ================================================================
echo                EVE ONLINE CRASH MONITOR STATUS
echo ================================================================
echo.

REM Change to project root directory
cd /d "%~dp0\.."

echo [INFO] Checking project structure...
if exist ".venv" (
    echo [OK] Virtual environment exists
) else (
    echo [ERROR] Virtual environment missing - run scripts\install.bat
    goto :end
)

if exist "python\eve_crash_monitor.py" (
    echo [OK] Main monitor script found
) else (
    echo [ERROR] Main monitor script missing
    goto :end
)

if exist "powershell\eve_monitor.ps1" (
    echo [OK] PowerShell monitor script found
) else (
    echo [WARN] PowerShell monitor script missing
)

echo.
echo [INFO] Testing virtual environment...
.venv\Scripts\python.exe --version
if errorlevel 1 (
    echo [ERROR] Virtual environment Python not working
    goto :end
) else (
    echo [OK] Virtual environment Python working
)

echo.
echo [INFO] Testing dependencies...
.venv\Scripts\python.exe -c "import psutil; print('[OK] psutil version:', psutil.__version__)"
if errorlevel 1 (
    echo [ERROR] psutil not available
    goto :end
)

.venv\Scripts\python.exe -c "import win32evtlog; print('[OK] pywin32 available')"
if errorlevel 1 (
    echo [ERROR] pywin32 not available
    goto :end
)

echo.
echo [INFO] Running installation test...
.venv\Scripts\python.exe python\test_installation.py
if errorlevel 1 (
    echo [ERROR] Installation test failed
    goto :end
)

echo.
echo ================================================================
echo                    SYSTEM READY
echo ================================================================
echo.
echo Your Eve Online Crash Monitor is ready to use!
echo.
echo To start monitoring:
echo   Option 1: scripts\run_monitor.bat      (Python Advanced Monitor)
echo   Option 2: powershell\eve_monitor.ps1   (PowerShell Monitor)
echo.
echo For help and documentation:
echo   - README.md                            (Main documentation)
echo   - docs\VIRTUAL_ENVIRONMENT_GUIDE.md   (Environment help)
echo   - docs\PYTHON_README.md                (Python monitor details)
echo.

:end
pause
