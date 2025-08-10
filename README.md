# Eve Online Crash Monitor

A comprehensive crash detection system for Eve Online that monitors for silent crashes and system failures without visible error dialogs.

## 🎯 Overview

This project provides dual monitoring solutions to detect Eve Online crashes that don't show traditional error messages:

- **Python Monitor**: Advanced monitoring with Windows Event Log integration and comprehensive crash analysis
- **PowerShell Monitor**: Lightweight real-time process monitoring with minimal dependencies
- **Centralized Logging**: All monitoring data saved to structured JSON and log files

## 📁 Project Structure

```
📁 eve/
├── 📁 .venv/           # Virtual Python Environment
│   └── Scripts/        # Python executables
├── 📁 docs/            # 📚 Documentation
│   ├── FIXED_SUMMARY.md        # Complete fix documentation
│   ├── PYTHON_README.md        # Python implementation guide
│   └── POWERSHELL_README.md    # PowerShell implementation guide
├── 📁 logs/            # 📊 Active Log Directory
│   └── eve_crash_log.txt       # Real crash logs with actual data
├── 📁 powershell/      # 🔧 PowerShell Implementation
│   └── eve_monitor.ps1          # PowerShell crash monitor
├── 📁 python/          # 🐍 Python Implementation
│   ├── eve_crash_monitor.py     # ⭐ Main crash monitor (ACTIVE)
│   ├── simple_eve_monitor.py   # Simple version for testing
│   ├── test_monitor.py          # Test scripts
│   ├── crash_monitor_config.json # Python configuration
│   └── requirements.txt         # Python dependencies
├── 📁 scripts/         # 🚀 Launch & Setup Scripts
│   ├── install.bat              # Complete installation with venv
│   ├── run_monitor.bat          # Launch the crash monitor
│   └── setup.bat                # Additional setup utilities
└── README.md           # 📖 Main project documentation
```

## 🚀 Quick Start

### Option 1: Python Monitor (Recommended)

1. **Setup Environment**:
   ```powershell
   .\scripts\install.bat
   ```

2. **Run Advanced Monitor**:
   ```powershell
   .\scripts\run_monitor.bat
   ```

3. **Or Run Simple Monitor**:
   ```powershell
   E:\eve\.venv\Scripts\python.exe python\simple_eve_monitor.py
   ```

### Option 2: PowerShell Monitor

1. **Navigate to PowerShell folder**:
   ```powershell
   cd powershell
   ```

2. **Start monitoring**:
   ```powershell
   .\eve_monitor.ps1 -Action start
   ```

3. **Check status**:
   ```powershell
   .\eve_monitor.ps1 -Action status
   ```

## 🔍 Monitoring Features

### Python Advanced Monitor
- ✅ **Windows Event Log Analysis** - Scans for application crashes, system errors, and hardware failures
- ✅ **Process Memory Monitoring** - Tracks memory usage patterns and leaks
- ✅ **Multi-threaded Detection** - Concurrent monitoring of processes, events, and logs
- ✅ **Text-based Logging** - Human-readable logs for easy analysis and review
- ✅ **Configurable Alerts** - Customizable crash detection parameters
- ✅ **Historical Analysis** - Scans past events for crash patterns

### Python Simple Monitor
- ✅ **Lightweight Process Monitoring** - Uses built-in Windows tools (tasklist, wmic)
- ✅ **No External Dependencies** - Pure Python with standard library
- ✅ **Fast Detection** - Rapid process status checking
- ✅ **Basic Logging** - Simple text-based crash logs

### PowerShell Monitor
- ✅ **Real-time Process Tracking** - Live monitoring with immediate notifications
- ✅ **Background Job Support** - Runs continuously without blocking terminal
- ✅ **Interactive Status** - Easy start/stop/status commands
- ✅ **Native Windows Integration** - Uses PowerShell's built-in process cmdlets

## 📊 Log Files

All monitoring data is saved to the `logs/` folder:

- **`eve_crash_log.txt`** - Advanced monitor crash events in human-readable format
- **`eve_crash_log_simple.txt`** - Simple monitor crash events in text format
- **`eve_crash_monitor.log`** - Detailed monitoring logs with debug information
- **`eve_monitor_ps.log`** - PowerShell monitor activity logs
- **`simple_eve_monitor.log`** - Simple monitor operational logs

## ⚙️ Configuration

### Python Monitor Configuration
Edit `python/crash_monitor_config.json`:
```json
{
    "eve_process_name": "exefile.exe",
    "check_interval": 5,
    "enable_event_log_monitoring": true,
    "enable_memory_monitoring": true
}
```

### PowerShell Monitor Configuration
Modify variables in `powershell/eve_monitor.ps1`:
- `$ProcessName` - Target process name
- `$CheckInterval` - Monitoring frequency (seconds)
- `$LogFile` - Output log file path

## 🛠️ System Requirements

- **Windows 10/11** (required for Event Log integration)
- **Python 3.7+** (for Python monitors)
- **PowerShell 5.1+** (for PowerShell monitor)
- **Administrative privileges** (recommended for full Event Log access)

## 📋 Dependencies

### Python Dependencies
- `psutil` - Process and system monitoring
- `pywin32` - Windows API integration for Event Logs

### PowerShell Dependencies
- Built-in cmdlets only (no external modules required)

## 🔧 Troubleshooting

### Common Issues

1. **Permission Errors**: Run PowerShell as Administrator for full Event Log access
2. **Python Module Import Errors**: Ensure virtual environment is activated
3. **Process Not Found**: Verify Eve Online process name in configuration

### Debug Mode
Run monitors with verbose logging:
```powershell
# Python
python eve_crash_monitor.py --debug

# PowerShell
.\eve_monitor.ps1 -Action start -Verbose
```

## 📈 Performance Impact

- **Python Advanced Monitor**: ~2-5% CPU during active monitoring
- **Python Simple Monitor**: ~1-2% CPU during monitoring
- **PowerShell Monitor**: ~1-3% CPU during monitoring
- **Memory Usage**: <50MB for all monitors combined

## 🎮 Eve Online Integration

The monitors are designed to detect:
- Silent application crashes without error dialogs
- Memory-related crashes and freezes
- Graphics driver failures
- System instability affecting game performance
- Network disconnection issues leading to crashes

## 📝 License

MIT License

Copyright (c) 2024 Eve Online Crash Monitor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🤝 Contributing

This is a personal monitoring solution, but feedback and improvements are welcome:
1. Test the monitors with your Eve Online setup
2. Report any false positives or missed crashes
3. Suggest additional monitoring features
4. Share configuration optimizations

## 📞 Support

For issues or questions:
1. Check the component-specific README files in `docs/` folder
2. Review log files in the `logs/` folder for error details
3. Ensure all system requirements are met
4. Verify Eve Online process name matches your installation

---

**Happy monitoring, capsuleer! Fly safe and crash-free! 🚀**
