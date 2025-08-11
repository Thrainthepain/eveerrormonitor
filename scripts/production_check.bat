@echo off
echo ===============================================
echo Eve Online Crash Monitor - Production Check
echo ===============================================
echo.

cd /d "%~dp0\.."

set "ERRORS=0"

echo [1/7] Checking project structure...
if exist "config\crash_monitor_config.json" (
    echo ✅ Configuration file exists
) else (
    echo ❌ Configuration file missing
    set /a ERRORS+=1
)

if exist "python\eve_crash_monitor.py" (
    echo ✅ Main monitor script exists
) else (
    echo ❌ Main monitor script missing
    set /a ERRORS+=1
)

if exist "python\crash_monitor_gui.py" (
    echo ✅ GUI interface exists
) else (
    echo ❌ GUI interface missing
    set /a ERRORS+=1
)

echo.
echo [2/7] Checking virtual environment...
if exist ".venv\Scripts\python.exe" (
    echo ✅ Virtual environment exists
    .venv\Scripts\python.exe --version
) else (
    echo ❌ Virtual environment missing - run scripts\install.bat
    set /a ERRORS+=1
)

echo.
echo [3/7] Checking dependencies...
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -c "import psutil" 2>nul && (
        echo ✅ psutil available
    ) || (
        echo ❌ psutil missing
        set /a ERRORS+=1
    )
    .venv\Scripts\python.exe -c "import win32evtlog" 2>nul && (
        echo ✅ pywin32 available
    ) || (
        echo ⚠️ pywin32 missing (optional)
    )
) else (
    echo ❌ Cannot check dependencies - virtual environment missing
    set /a ERRORS+=1
)

echo.
echo [4/7] Testing Python imports...
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -c "import sys; sys.path.append('python'); from eve_crash_monitor import EveOnlineCrashMonitor" 2>nul && (
        echo ✅ eve_crash_monitor imports successfully
    ) || (
        echo ❌ eve_crash_monitor import failed
        set /a ERRORS+=1
    )
    .venv\Scripts\python.exe -c "import sys; sys.path.append('python'); from crash_monitor_gui import CrashMonitorGUI" 2>nul && (
        echo ✅ crash_monitor_gui imports successfully
    ) || (
        echo ❌ crash_monitor_gui import failed
        set /a ERRORS+=1
    )
) else (
    echo ❌ Cannot test imports - virtual environment missing
    set /a ERRORS+=1
)

echo.
echo [5/7] Checking scripts...
for %%f in (install.bat setup.bat run_gui.bat run_monitor.bat status.bat) do (
    if exist "scripts\%%f" (
        echo ✅ scripts\%%f exists
    ) else (
        echo ❌ scripts\%%f missing
        set /a ERRORS+=1
    )
)

echo.
echo [6/7] Checking directories...
if exist "logs" (
    echo ✅ logs directory exists
) else (
    echo ⚠️ logs directory missing - will be created on first run
)

if exist "config" (
    echo ✅ config directory exists
) else (
    echo ❌ config directory missing
    set /a ERRORS+=1
)

echo.
echo [7/7] Final production readiness check...
if %ERRORS% GTR 0 (
    echo.
    echo ❌ PRODUCTION CHECK FAILED
    echo Found %ERRORS% issue(s) that need to be fixed.
    echo Please fix the issues above before deployment.
    exit /b 1
) else (
    echo.
    echo ✅ PRODUCTION CHECK PASSED
    echo All components are ready for production use!
    echo.
    echo You can now run:
    echo   - scripts\run_gui.bat (GUI interface)
    echo   - scripts\run_monitor.bat (command line)
)

echo.
pause
