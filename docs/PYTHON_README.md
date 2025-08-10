# Python Monitoring System

Advanced crash detection using Python with full Windows integration.

## Files

- **`python/eve_crash_monitor.py`** - Main advanced monitor with all features
- **`python/simple_eve_monitor.py`** - Lightweight monitor using built-in tools only
- **`python/test_monitor.py`** - Testing framework for validation
- **`python/requirements.txt`** - Python dependencies
- **`python/crash_monitor_config.json`** - Configuration file

## Installation

```bash
# Run the automated installer from project root
.\scripts\install.bat
```

## Dependencies

- **psutil** - Process and system monitoring
- **pywin32** - Windows Event Log integration

## Usage

### Advanced Monitor
```bash
# From project root
.\scripts\run_monitor.bat

# Or manually
E:\eve\.venv\Scripts\python.exe python\eve_crash_monitor.py
```

Interactive commands:
- `start` - Begin monitoring
- `stop` - Stop monitoring  
- `report` - Generate crash report
- `status` - Show current status
- `quit` - Exit program

### Simple Monitor
```bash
# From project root
E:\eve\.venv\Scripts\python.exe python\simple_eve_monitor.py
```

## Configuration

Edit `python/crash_monitor_config.json`:

```json
{
    "check_interval": 5,
    "process_names": ["ExeFile.exe", "eve.exe"],
    "log_level": "INFO",
    "enable_event_log_monitoring": true,
    "enable_process_monitoring": true,
    "enable_log_file_monitoring": true,
    "crash_detection_threshold": 30,
    "output_file": "eve_crash_log.txt"
}
```

## Output

Logs are saved to `../logs/` directory:
- `eve_crash_monitor.log` - Activity log
- `eve_crash_log.txt` - Detected crashes in human-readable text format
