# Virtual Environment Management Guide

Complete guide for managing the Python virtual environment used by the Eve Online Crash Monitor.

## 🎯 What is a Virtual Environment?

A **virtual environment** is an isolated Python installation that keeps this project's dependencies separate from your system Python. This prevents conflicts and ensures consistent behavior.

## 📍 Location

The virtual environment is located at:
```
E:\eve\.venv\
```

## ✅ Quick Health Check

Run this command to verify everything is working:

```powershell
E:\eve\.venv\Scripts\python.exe -c "import psutil, win32evtlog; print('✅ Virtual environment is healthy!')"
```

## 🔧 Common Tasks

### Check if Virtual Environment Exists

```powershell
# From the E:\eve\ directory
Test-Path ".\.venv"
```

**Expected Result**: `True`

### View Installed Packages

```powershell
E:\eve\.venv\Scripts\pip.exe list
```

**Expected Packages**:
- `psutil` (process monitoring)
- `pywin32` (Windows Event Log access)
- `pip` (package manager)
- `setuptools` (installation tools)

### Check Python Version

```powershell
E:\eve\.venv\Scripts\python.exe --version
```

**Minimum Required**: Python 3.7+

## 🚀 Setup Methods

### Method 1: Automated Setup (Recommended)

```powershell
# Run the complete installer
.\scripts\install.bat
```

This will:
1. Create virtual environment
2. Install all dependencies
3. Verify installation
4. Set up launch scripts

### Method 2: Manual Setup

If you need to set up manually:

```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Install requirements
.\.venv\Scripts\pip.exe install -r python\requirements.txt

# 3. Verify installation
.\.venv\Scripts\python.exe -c "import psutil, win32evtlog; print('Setup complete!')"
```

## 🏃‍♂️ Running Python Scripts

### Option 1: Direct Execution (Recommended)

Always use the full path to the virtual environment Python:

```powershell
# Run the main monitor
E:\eve\.venv\Scripts\python.exe python\eve_crash_monitor.py

# Run the simple monitor
E:\eve\.venv\Scripts\python.exe python\simple_eve_monitor.py

# Run tests
E:\eve\.venv\Scripts\python.exe python\test_monitor.py
```

### Option 2: Using Activation

You can activate the virtual environment to use `python` commands directly:

```powershell
# Activate
.\.venv\Scripts\Activate.ps1

# Now you can use python directly
python python\eve_crash_monitor.py

# Deactivate when done
deactivate
```

**Note**: Direct execution (Option 1) is preferred as it's more reliable.

## 🐛 Troubleshooting

### Problem: "python is not recognized as an internal or external command"

**Cause**: Windows can't find the Python executable.

**Solution**: Use the full path:
```powershell
E:\eve\.venv\Scripts\python.exe python\eve_crash_monitor.py
```

### Problem: "No module named 'psutil'" or "No module named 'win32evtlog'"

**Cause**: Dependencies not installed in virtual environment.

**Solution**: Reinstall dependencies:
```powershell
E:\eve\.venv\Scripts\pip.exe install -r python\requirements.txt
```

### Problem: "cannot be loaded because running scripts is disabled"

**Cause**: PowerShell execution policy restriction.

**Solution**: Set execution policy:
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: Virtual environment is corrupted

**Symptoms**: 
- Import errors
- Missing files in `.venv` directory
- Python executable not working

**Solution**: Remove and recreate:
```powershell
# Remove corrupted environment
Remove-Item -Recurse -Force .venv

# Recreate everything
.\scripts\install.bat
```

### Problem: Permission denied during installation

**Cause**: Insufficient permissions.

**Solutions**:
1. Run PowerShell as Administrator
2. Check antivirus isn't blocking installation
3. Ensure disk has sufficient space

### Problem: Installation fails on Windows

**Common fixes**:
```powershell
# Update pip first
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# Install with verbose output to see errors
.\.venv\Scripts\pip.exe install -r python\requirements.txt -v

# Force reinstall if needed
.\.venv\Scripts\pip.exe install -r python\requirements.txt --force-reinstall
```

## 📊 Virtual Environment Status Script

Save this as `check_venv.ps1` for detailed status checking:

```powershell
# Virtual Environment Health Check
# Run from E:\eve\ directory

Write-Host "🔍 Checking Virtual Environment Status..." -ForegroundColor Cyan
Write-Host ""

# Check 1: Directory exists
if (Test-Path ".\.venv") {
    Write-Host "✅ Virtual environment directory exists" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment directory missing" -ForegroundColor Red
    Write-Host "   Run: .\scripts\install.bat" -ForegroundColor Yellow
    exit 1
}

# Check 2: Python executable
Write-Host "🐍 Testing Python executable..." -ForegroundColor Cyan
try {
    $pythonVersion = & ".\.venv\Scripts\python.exe" --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python works: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python executable failed"
    }
} catch {
    Write-Host "❌ Python executable not working" -ForegroundColor Red
    Write-Host "   Run: .\scripts\install.bat" -ForegroundColor Yellow
}

# Check 3: Package availability
Write-Host "📦 Testing required packages..." -ForegroundColor Cyan
try {
    & ".\.venv\Scripts\python.exe" -c "import psutil" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ psutil package available" -ForegroundColor Green
    } else {
        throw "psutil import failed"
    }
} catch {
    Write-Host "❌ psutil package missing" -ForegroundColor Red
}

try {
    & ".\.venv\Scripts\python.exe" -c "import win32evtlog" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pywin32 package available" -ForegroundColor Green
    } else {
        throw "pywin32 import failed"
    }
} catch {
    Write-Host "❌ pywin32 package missing" -ForegroundColor Red
    Write-Host "   Run: .\.venv\Scripts\pip.exe install -r python\requirements.txt" -ForegroundColor Yellow
}

# Check 4: Monitor script accessibility
Write-Host "🖥️ Testing monitor script..." -ForegroundColor Cyan
if (Test-Path "python\eve_crash_monitor.py") {
    Write-Host "✅ Main monitor script found" -ForegroundColor Green
} else {
    Write-Host "❌ Main monitor script missing" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Virtual Environment Status Check Complete!" -ForegroundColor Cyan
```

## 🚀 Quick Commands Reference

```powershell
# Setup virtual environment
.\scripts\install.bat

# Run crash monitor (recommended method)
.\scripts\run_monitor.bat

# Manual execution
E:\eve\.venv\Scripts\python.exe python\eve_crash_monitor.py

# Check virtual environment health
E:\eve\.venv\Scripts\python.exe -c "import psutil, win32evtlog; print('OK')"

# List installed packages
E:\eve\.venv\Scripts\pip.exe list

# Update packages
E:\eve\.venv\Scripts\pip.exe install -r python\requirements.txt --upgrade

# Remove virtual environment
Remove-Item -Recurse -Force .venv
```

## 💡 Best Practices

1. **Always use the installer**: `.\scripts\install.bat` handles everything correctly
2. **Use direct execution**: More reliable than activation/deactivation
3. **Check health regularly**: Run the status check script periodically
4. **Don't modify manually**: Let the scripts manage the virtual environment
5. **Use full paths**: Avoid "python not found" errors

## 🔗 Related Documentation

- **Main README**: Overall project documentation
- **Python README**: Python-specific implementation details
- **Installation Scripts**: Automated setup and execution scripts

---

**Remember**: The virtual environment ensures your Eve Online crash monitor works reliably regardless of your system Python configuration!
