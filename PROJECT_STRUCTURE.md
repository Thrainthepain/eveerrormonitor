# Eve Online Crash Monitor - Project Structure

## Overview

This document outlines the complete project structure, emphasizing the clean separation between original CCP Games files and our custom crash monitoring implementations.

## Directory Structure

```
📁 eve/
├── 📁 .venv/                    # Python Virtual Environment
│   ├── Scripts/                 # Python executables and activation scripts
│   ├── Lib/                     # Installed Python packages
│   └── pyvenv.cfg              # Virtual environment configuration
│
├── 📁 .github/                  # GitHub Configuration
│   ├── workflows/               # CI/CD workflows
│   └── dependabot.yml          # Dependency monitoring
│
├── 📁 docs/                     # 📚 Project Documentation
│   ├── FIXED_SUMMARY.md        # Complete bug fix documentation
│   ├── PYTHON_README.md        # Python implementation guide
│   ├── POWERSHELL_README.md    # PowerShell implementation guide
│   └── VIRTUAL_ENVIRONMENT_GUIDE.md # venv management guide
│
├── 📁 EveLogLite-master/        # 🎯 CCP Games Official Files (UNTOUCHED)
│   ├── 📁 src/                  # Original C++ Qt source code
│   │   ├── main.cpp             # Main application entry point
│   │   ├── mainwindow.cpp       # Primary GUI window
│   │   ├── logmodel.cpp         # Log data model
│   │   ├── logview.cpp          # Log display widget
│   │   ├── filterdialog.cpp     # Log filtering system
│   │   ├── mainwindow.ui        # Qt UI definition files
│   │   ├── LogLite.pro          # Qt project file
│   │   └── resources/           # GUI resources (icons, etc.)
│   ├── 📁 clients/              # Client library implementations
│   │   ├── python/              # Original Python 2 client
│   │   │   └── __init__.py      # Network protocol client
│   │   └── qtclient/            # Qt-based client
│   ├── LICENSE                  # CCP Games license
│   ├── README.md               # Original CCP documentation
│   ├── INTEGRATION_README.md   # Our integration guide
│   └── .gitignore              # CCP's original git ignore
│
├── 📁 logs/                     # 📊 Active Logging Directory
│   ├── eve_crash_log.txt        # Main crash log (text format)
│   ├── eve_crash_log.json       # Legacy JSON format
│   ├── .gitignore               # Excludes personal logs from git
│   └── (various runtime logs)   # Generated during monitoring
│
├── 📁 powershell/               # 🔧 PowerShell Implementation
│   ├── eve_monitor.ps1          # PowerShell crash monitor
│   └── README.md               # PowerShell specific documentation
│
├── 📁 python/                   # 🐍 Python Implementation
│   ├── eve_crash_monitor.py     # ⭐ Main crash monitor (Advanced)
│   ├── crash_monitor_gui.py     # ⭐ GUI interface (NEW)
│   ├── enhanced_crash_monitor.py # ⭐ EveLogLite integration (NEW)
│   ├── eveloglite_client.py     # Modernized CCP client for Python 3
│   ├── simple_eve_monitor.py    # Lightweight monitor for testing
│   ├── test_monitor.py          # Monitor functionality tests
│   ├── test_installation.py     # Installation verification script
│   ├── crash_monitor_config.json # Configuration file (auto-generated)
│   ├── simple_monitor_config.json # Simple monitor configuration
│   └── requirements.txt         # Python dependencies
│
├── 📁 scripts/                  # 🚀 Launch & Setup Scripts
│   ├── install.bat              # Complete installation with venv setup
│   ├── run_gui.bat              # ⭐ Launch GUI monitor (NEW)
│   ├── run_monitor.bat          # Launch command-line monitor
│   ├── run_simple_monitor.bat   # Launch lightweight monitor
│   └── setup.bat                # Additional setup utilities
│
├── CONVERSION_SUMMARY.md        # Data format conversion documentation
├── FIXED_SUMMARY.md            # Complete bug resolution log
├── PROJECT_STRUCTURE.md        # This file
├── README.md                   # 📖 Main project documentation
├── SECURITY.md                 # Security policy and guidelines
├── requirements.txt            # Top-level Python dependencies
└── .gitignore                  # Project-wide git exclusions
```

## File Categories

### 🎯 CCP Games Original Files
**Location**: `EveLogLite-master/`
- **Status**: UNTOUCHED - Preserved exactly as provided by CCP
- **Purpose**: Official Eve Online log viewer with professional GUI
- **Technology**: C++ with Qt framework
- **License**: CCP Games license

### 🐍 Our Python Implementation
**Location**: `python/`
- **eve_crash_monitor.py**: Advanced crash detection with Windows Event Log integration
- **crash_monitor_gui.py**: Modern tkinter-based GUI interface
- **enhanced_crash_monitor.py**: Integrates with CCP's EveLogLite
- **eveloglite_client.py**: Modernized Python 3 version of CCP's client
- **simple_eve_monitor.py**: Lightweight monitoring for basic use cases

### 🚀 Launcher Scripts  
**Location**: `scripts/`
- **run_gui.bat**: Launch GUI interface (recommended for most users)
- **run_monitor.bat**: Launch command-line interface 
- **install.bat**: Complete setup with virtual environment

### 📊 Log Management
**Location**: `logs/`
- All runtime logs with `.gitignore` to protect privacy
- Text-based format for human readability
- Structured data with timestamps and process information

## Integration Architecture

### Standalone Operation
```
User → run_gui.bat → crash_monitor_gui.py → eve_crash_monitor.py → logs/
```

### EveLogLite Integration
```
User → EveLogLite.exe (CCP GUI) ← enhanced_crash_monitor.py ← eveloglite_client.py
                                           ↓
                                    eve_crash_monitor.py → logs/
```

## Key Design Principles

1. **Clean Separation**: CCP files remain untouched in their own directory
2. **Multiple Interfaces**: GUI, command-line, and EveLogLite integration
3. **Backward Compatibility**: All existing functionality preserved
4. **Privacy Protection**: Personal logs excluded from version control
5. **Professional Integration**: Works with official CCP tools while maintaining independence

## Development Guidelines

- **Never modify files in `EveLogLite-master/`** - These are CCP's original files
- **All custom code goes in `python/`** - Clean separation of responsibilities
- **Use virtual environment** - Isolated dependency management
- **Text-based logs** - Human-readable and version-control friendly
- **Comprehensive documentation** - Each component thoroughly documented
