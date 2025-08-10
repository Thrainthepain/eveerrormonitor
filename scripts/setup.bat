@echo off
title Eve Online Crash Monitor Setup
echo.
echo ================================================================
echo                  EVE ONLINE CRASH MONITOR SETUP
echo ================================================================
echo.
echo This tool will help you detect and analyze Eve Online crashes,
echo especially those that happen without visible error messages.
echo.
echo Available monitoring options:
echo.
echo 1. Simple Python Monitor (Recommended)
echo    - Lightweight and reliable
echo    - Works on most systems
echo    - JSON-based logging and reporting
echo.
echo 2. Full Python Monitor (Advanced)
echo    - More detailed analysis
echo    - Requires additional packages
echo    - Windows Event Log integration
echo.
echo 3. PowerShell Monitor (Alternative)
echo    - Uses built-in Windows PowerShell
echo    - Good for systems with Python issues
echo    - Background job monitoring
echo.
echo ================================================================
echo.

:menu
echo Choose your option:
echo [1] Setup Simple Python Monitor (Recommended)
echo [2] Setup Full Python Monitor (Advanced)
echo [3] Setup PowerShell Monitor
echo [4] Test existing installation
echo [5] View README and documentation
echo [Q] Quit
echo.
set /p choice="Enter your choice (1-5, Q): "

if /i "%choice%"=="1" goto simple_setup
if /i "%choice%"=="2" goto full_setup
if /i "%choice%"=="3" goto powershell_setup
if /i "%choice%"=="4" goto test_setup
if /i "%choice%"=="5" goto show_readme
if /i "%choice%"=="q" goto quit
echo Invalid choice. Please try again.
echo.
goto menu

:simple_setup
echo.
echo Setting up Simple Python Monitor...
echo ===================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    goto menu
)

echo ✓ Python found
echo.
echo Testing the simple monitor...
python test_monitor.py

if errorlevel 1 (
    echo.
    echo There was an issue with the test. Check the output above.
    pause
    goto menu
)

echo.
echo ✓ Simple monitor setup complete!
echo.
echo To start monitoring:
echo 1. Run: python simple_eve_monitor.py
echo 2. Type 'start' to begin monitoring
echo 3. Launch Eve Online
echo 4. Play normally - crashes will be detected automatically
echo 5. Type 'report' to see crash analysis
echo.
echo Would you like to start the monitor now? (Y/N)
set /p start_now=""
if /i "%start_now%"=="y" (
    echo.
    echo Starting monitor...
    python simple_eve_monitor.py
)
goto menu

:full_setup
echo.
echo Setting up Full Python Monitor...
echo =================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    goto menu
)

echo ✓ Python found
echo.
echo Installing required packages...
pip install psutil pywin32

if errorlevel 1 (
    echo.
    echo WARNING: Package installation failed.
    echo The simple monitor will still work with basic functionality.
    echo.
)

echo.
echo Testing the full monitor...
python -c "import eve_crash_monitor; print('✓ Full monitor imported successfully')"

if errorlevel 1 (
    echo.
    echo Full monitor test failed. Falling back to simple monitor.
    echo You can still use: python simple_eve_monitor.py
    pause
    goto menu
)

echo.
echo ✓ Full monitor setup complete!
echo.
echo To start monitoring:
echo 1. Run: python eve_crash_monitor.py
echo 2. Type 'start' to begin monitoring
echo 3. Launch Eve Online
echo.
echo Would you like to start the monitor now? (Y/N)
set /p start_now=""
if /i "%start_now%"=="y" (
    echo.
    echo Starting monitor...
    python eve_crash_monitor.py
)
goto menu

:powershell_setup
echo.
echo Setting up PowerShell Monitor...
echo ================================
echo.

powershell -Command "Write-Host 'Testing PowerShell execution...' -ForegroundColor Green"
if errorlevel 1 (
    echo ERROR: PowerShell is not available or execution policy restricts scripts
    echo.
    echo To fix this, run PowerShell as Administrator and execute:
    echo Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    echo.
    pause
    goto menu
)

echo ✓ PowerShell available
echo.
echo Testing PowerShell monitor...
powershell -File eve_monitor.ps1 -Action status

echo.
echo ✓ PowerShell monitor setup complete!
echo.
echo To start monitoring:
echo 1. Run: powershell -File eve_monitor.ps1
echo 2. Type 'start' to begin monitoring
echo 3. Launch Eve Online
echo.
echo Would you like to start the monitor now? (Y/N)
set /p start_now=""
if /i "%start_now%"=="y" (
    echo.
    echo Starting PowerShell monitor...
    powershell -File eve_monitor.ps1
)
goto menu

:test_setup
echo.
echo Testing existing installation...
echo ===============================
echo.

echo Testing Python availability...
python --version
if errorlevel 1 (
    echo ✗ Python not found
) else (
    echo ✓ Python available
)

echo.
echo Testing monitors...
python test_monitor.py

echo.
echo Testing PowerShell...
powershell -Command "Write-Host 'PowerShell test successful' -ForegroundColor Green"

echo.
echo Test complete. Check the output above for any issues.
pause
goto menu

:show_readme
echo.
echo Opening documentation...
if exist README.md (
    start notepad README.md
) else (
    echo README.md not found in current directory
)
echo.
echo Key points:
echo - Leave the monitor running while playing Eve Online
echo - Crashes under 30 seconds runtime are flagged as suspicious
echo - Check 'report' command for crash analysis
echo - High memory usage warnings are normal for Eve Online
echo.
pause
goto menu

:quit
echo.
echo Thanks for using the Eve Online Crash Monitor!
echo.
echo Remember:
echo - Run the monitor whenever you play Eve Online
echo - Use the 'report' command to analyze crash patterns
echo - Check log files if you need detailed information
echo.
echo Fly safe! o7
pause
exit /b 0
