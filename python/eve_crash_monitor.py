#!/usr/bin/env python3
"""
Eve Online Crash Monitor
A comprehensive tool to detect and analyze Eve Online crashes even when no obvious errors appear.
"""

import os
import sys
import time
import json
import logging
import threading
import winreg
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Optional imports for advanced features
try:
    import psutil  # type: ignore
    psutil_available = True
except ImportError:
    psutil_available = False
    psutil = None  # type: ignore
    print("Warning: psutil not available. Some features will be limited.")

try:
    import win32evtlog  # type: ignore
    win32_available = True
except ImportError:
    win32_available = False
    win32evtlog = None  # type: ignore
    print("Warning: win32evtlog not available. Event log monitoring disabled.")

class EveOnlineCrashMonitor:
    def __init__(self, config_file: str = "crash_monitor_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_logging()
        self.eve_processes: Dict[int, Dict[str, Any]] = {}
        self.monitoring = False
        self.log_locations = self.discover_eve_log_locations()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default config."""
        default_config: Dict[str, Any] = {
            "check_interval": 5,  # seconds
            "process_names": ["ExeFile.exe", "eve.exe"],
            "log_level": "INFO",
            "enable_event_log_monitoring": True,
            "enable_process_monitoring": True,
            "enable_log_file_monitoring": True,
            "crash_detection_threshold": 30,  # seconds
            "output_file": "../logs/eve_crash_log.txt"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return default_config
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../logs/eve_crash_monitor.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def discover_eve_log_locations(self) -> List[Path]:
        """Discover potential Eve Online log locations."""
        locations: List[Path] = []
        
        # Common Eve Online installation paths
        common_paths = [
            Path(os.environ.get('LOCALAPPDATA', '')) / "CCP" / "EVE",
            Path(os.environ.get('PROGRAMFILES', '')) / "CCP" / "EVE",
            Path(os.environ.get('PROGRAMFILES(X86)', '')) / "CCP" / "EVE",
            Path("C:/EVE"),
            Path("D:/EVE"),
            Path("E:/EVE")
        ]
        
        # Add Steam installation path
        try:
            steam_path = self.get_steam_eve_path()
            if steam_path:
                common_paths.append(Path(steam_path))
        except Exception as e:
            self.logger.debug(f"Could not get Steam path: {e}")
        
        # Check for log directories
        for base_path in common_paths:
            if base_path.exists():
                log_dirs = [
                    base_path / "logs",
                    base_path / "cache",
                    base_path / "LogServer",
                    base_path
                ]
                for log_dir in log_dirs:
                    if log_dir.exists():
                        locations.append(log_dir)
        
        return locations
    
    def get_steam_eve_path(self) -> Optional[str]:
        """Get Eve Online path from Steam registry."""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 8500")
            path, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)
            return path
        except FileNotFoundError:
            return None
    
    def get_running_eve_processes(self) -> List[Any]:
        """Get list of running Eve Online processes."""
        if not psutil_available or psutil is None:
            return []
            
        eve_processes: List[Any] = []
        process_names = self.config.get("process_names", ["ExeFile.exe", "eve.exe"])
        
        try:
            # Use psutil directly since it's already imported at module level
            attrs = ['pid', 'name', 'create_time', 'memory_info', 'cpu_percent']
            # Type ignore for process_iter as it's an optional import
            for proc in psutil.process_iter(attrs):  # type: ignore
                try:
                    if proc.info and proc.info.get('name', '').lower() in [name.lower() for name in process_names]:
                        eve_processes.append(proc)
                except Exception:
                    # Handle any psutil exceptions (NoSuchProcess, AccessDenied, etc.)
                    continue
        except Exception:
            # If psutil fails, return empty list
            pass
        
        return eve_processes
    
    def monitor_processes(self):
        """Monitor Eve Online processes for unexpected termination."""
        if not psutil_available:
            self.logger.warning("Process monitoring disabled - psutil not available")
            return
            
        while self.monitoring:
            try:
                current_processes = self.get_running_eve_processes()
                current_pids = {proc.pid for proc in current_processes}
                
                # Check for new processes
                for proc in current_processes:
                    if proc.pid not in self.eve_processes:
                        try:
                            memory_usage = proc.memory_info().rss if proc.is_running() else 0
                        except Exception:
                            memory_usage = 0
                            
                        self.eve_processes[proc.pid] = {
                            'process': proc,
                            'start_time': datetime.now(),
                            'last_seen': datetime.now(),
                            'memory_usage': memory_usage,
                            'cpu_usage': 0
                        }
                        self.logger.info(f"New Eve process detected: PID {proc.pid}")
                
                # Check for terminated processes
                terminated_pids = set(self.eve_processes.keys()) - current_pids
                for pid in terminated_pids:
                    process_info = self.eve_processes[pid]
                    runtime = datetime.now() - process_info['start_time']
                    
                    crash_data: Dict[str, Any] = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'process_termination',
                        'pid': pid,
                        'runtime_seconds': runtime.total_seconds(),
                        'start_time': process_info['start_time'].isoformat(),
                        'end_time': datetime.now().isoformat(),
                        'memory_usage_mb': process_info['memory_usage'] / (1024 * 1024),
                        'suspected_crash': runtime.total_seconds() < self.config.get('crash_detection_threshold', 30)
                    }
                    
                    self.log_crash_event(crash_data)
                    
                    if crash_data['suspected_crash']:
                        self.logger.warning(f"Potential crash detected: Eve process {pid} terminated after {runtime.total_seconds():.1f} seconds")
                    else:
                        self.logger.info(f"Eve process {pid} terminated normally after {runtime.total_seconds():.1f} seconds")
                    
                    del self.eve_processes[pid]
                
                # Update existing processes
                for proc in current_processes:
                    if proc.pid in self.eve_processes:
                        try:
                            self.eve_processes[proc.pid]['last_seen'] = datetime.now()
                            self.eve_processes[proc.pid]['memory_usage'] = proc.memory_info().rss
                            self.eve_processes[proc.pid]['cpu_usage'] = proc.cpu_percent()
                        except Exception:
                            pass
                
                time.sleep(self.config.get("check_interval", 5))
                
            except Exception as e:
                self.logger.error(f"Error in process monitoring: {e}")
                time.sleep(5)
    
    def monitor_event_logs(self):
        """Monitor Windows Event Logs for application crashes."""
        if not self.config.get("enable_event_log_monitoring", True):
            return
            
        last_check = datetime.now() - timedelta(minutes=5)
        
        while self.monitoring:
            try:
                # Check Application Event Log
                events = self.get_recent_crash_events(last_check)
                for event in events:
                    self.log_crash_event(event)
                    self.logger.warning(f"Windows Event Log crash detected: {event}")
                
                last_check = datetime.now()
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring event logs: {e}")
                time.sleep(30)
    
    def get_recent_crash_events(self, since: datetime) -> List[Dict[str, Any]]:
        """Get recent crash events from Windows Event Log."""
        if not win32_available or win32evtlog is None:
            return []
            
        crash_events: List[Dict[str, Any]] = []
        
        try:
            server = 'localhost'
            logtype = 'Application'
            hand = win32evtlog.OpenEventLog(server, logtype)
            
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            
            for event in events:
                if event.TimeGenerated > since:
                    # Look for application error events
                    if (event.EventType == win32evtlog.EVENTLOG_ERROR_TYPE and 
                        event.SourceName and 
                        ('eve' in event.SourceName.lower() or 
                         'exefile' in event.SourceName.lower() or
                         event.EventID in [1000, 1001])):  # Application Error events
                        
                        crash_data: Dict[str, Any] = {
                            'timestamp': event.TimeGenerated.isoformat(),
                            'type': 'windows_event_log',
                            'event_id': event.EventID,
                            'source': event.SourceName,
                            'description': str(event.StringInserts) if event.StringInserts else "No description",
                            'category': event.EventCategory
                        }
                        crash_events.append(crash_data)
            
            win32evtlog.CloseEventLog(hand)
            
        except Exception as e:
            self.logger.debug(f"Error reading event log: {e}")
        
        return crash_events
    
    def monitor_log_files(self):
        """Monitor Eve Online log files for error patterns."""
        if not self.config.get("enable_log_file_monitoring", True):
            return
            
        file_positions: Dict[str, int] = {}
        error_patterns = [
            "exception", "error", "crash", "fault", "violation",
            "access violation", "memory error", "stack overflow",
            "assertion failed", "fatal error", "unhandled exception"
        ]
        
        # Files to exclude from monitoring (our own logs)
        exclude_files = [
            "eve_crash_monitor.log",
            "eve_crash_log.txt"
        ]
        
        while self.monitoring:
            try:
                for log_location in self.log_locations:
                    if not log_location.exists():
                        continue
                        
                    for log_file in log_location.glob("*.log"):
                        try:
                            # Skip our own log files to avoid infinite loops
                            if (log_file.name in exclude_files or 
                                'eve_crash_monitor.log' in str(log_file) or
                                'eve_crash_log.txt' in str(log_file)):
                                continue
                                
                            # Track file position to only read new content
                            current_size = log_file.stat().st_size
                            last_position = file_positions.get(str(log_file), 0)
                            
                            if current_size > last_position:
                                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    f.seek(last_position)
                                    new_content = f.read()
                                    
                                    # Look for error patterns
                                    lines = new_content.split('\n')
                                    for i, line in enumerate(lines):
                                        line_lower = line.lower()
                                        for pattern in error_patterns:
                                            if pattern in line_lower:
                                                crash_data: Dict[str, Any] = {
                                                    'timestamp': datetime.now().isoformat(),
                                                    'type': 'log_file_error',
                                                    'file': str(log_file),
                                                    'line_number': last_position + i + 1,
                                                    'content': line.strip(),
                                                    'pattern_matched': pattern
                                                }
                                                self.log_crash_event(crash_data)
                                                self.logger.warning(f"Error pattern '{pattern}' found in {log_file}: {line.strip()}")
                                
                                file_positions[str(log_file)] = current_size
                        
                        except Exception as e:
                            self.logger.debug(f"Error reading log file {log_file}: {e}")
                
                time.sleep(10)  # Check log files every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in log file monitoring: {e}")
                time.sleep(10)
    
    def log_crash_event(self, crash_data: Dict[str, Any]):
        """Log crash event to output file."""
        output_file = self.config.get("output_file", "eve_crash_log.txt")
        
        try:
            # Format crash data as human-readable text
            timestamp = crash_data.get("timestamp", datetime.now().isoformat())
            crash_type = crash_data.get("type", "Unknown")
            
            # Handle different data structures based on crash type
            if crash_type == "process_termination":
                # Process monitoring data
                log_entry = f"""
{'='*80}
CRASH DETECTED: {timestamp}
{'='*80}
Crash Type: Process Termination
Process ID: {crash_data.get('pid', 'Unknown')}
Runtime: {crash_data.get('runtime_seconds', 'Unknown')} seconds
Memory Usage: {crash_data.get('memory_usage_mb', 'Unknown'):.1f} MB
Start Time: {crash_data.get('start_time', 'Unknown')}
End Time: {crash_data.get('end_time', 'Unknown')}
Suspected Crash: {crash_data.get('suspected_crash', 'Unknown')}

Additional Details: Process terminated {"abnormally" if crash_data.get('suspected_crash') else "normally"}
{'='*80}

"""
            elif crash_type == "windows_event_log":
                # Event log monitoring data
                log_entry = f"""
{'='*80}
CRASH DETECTED: {timestamp}
{'='*80}
Crash Type: Windows Event Log Error
Event ID: {crash_data.get('event_id', 'Unknown')}
Source: {crash_data.get('source', 'Unknown')}
Category: {crash_data.get('category', 'Unknown')}
Description: {crash_data.get('description', 'No description available')}

Additional Details: System event log crash detection
{'='*80}

"""
            elif crash_type == "log_file_error":
                # File monitoring data
                log_entry = f"""
{'='*80}
CRASH DETECTED: {timestamp}
{'='*80}
Crash Type: Log File Error Pattern
File: {crash_data.get('file', 'Unknown')}
Line Number: {crash_data.get('line_number', 'Unknown')}
Pattern Matched: {crash_data.get('pattern_matched', 'Unknown')}
Content: {crash_data.get('content', 'No content available')}

Additional Details: Error pattern detected in Eve Online log files
{'='*80}

"""
            else:
                # Fallback for unknown types (original format)
                process_info = crash_data.get("process_info", {})
                event_info = crash_data.get("event_log_info", {})
                
                log_entry = f"""
{'='*80}
CRASH DETECTED: {timestamp}
{'='*80}
Crash Type: {crash_type}
Process ID: {process_info.get('pid', crash_data.get('pid', 'Unknown'))}
Process Name: {process_info.get('name', 'Unknown')}
Memory Usage: {process_info.get('memory_mb', 'Unknown')} MB
CPU Usage: {process_info.get('cpu_percent', 'Unknown')}%
Running Time: {process_info.get('running_time_seconds', 'Unknown')} seconds

Event Log Information:
- Event ID: {event_info.get('event_id', crash_data.get('event_id', 'N/A'))}
- Source: {event_info.get('source', crash_data.get('source', 'N/A'))}
- Level: {event_info.get('level', 'N/A')}
- Message: {event_info.get('message', 'N/A')}

Additional Details: {crash_data.get('details', 'No additional details')}
{'='*80}

"""
            
            # Append to log file
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            self.logger.error(f"Error logging crash event: {e}")
    
    def start_monitoring(self) -> List[Any]:
        """Start all monitoring threads."""
        if self.monitoring:
            self.logger.warning("Monitoring is already running")
            return []
        
        self.monitoring = True
        self.logger.info("Starting Eve Online crash monitoring...")
        
        threads: List[Any] = []
        
        if self.config.get("enable_process_monitoring", True):
            process_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            threads.append(process_thread)
            process_thread.start()
            self.logger.info("Started process monitoring")
        
        if self.config.get("enable_event_log_monitoring", True):
            event_thread = threading.Thread(target=self.monitor_event_logs, daemon=True)
            threads.append(event_thread)
            event_thread.start()
            self.logger.info("Started Windows Event Log monitoring")
        
        if self.config.get("enable_log_file_monitoring", True):
            log_thread = threading.Thread(target=self.monitor_log_files, daemon=True)
            threads.append(log_thread)
            log_thread.start()
            self.logger.info("Started log file monitoring")
        
        return threads
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False
        self.logger.info("Stopped Eve Online crash monitoring")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a crash report from logged events."""
        output_file = self.config.get("output_file", "eve_crash_log.txt")
        
        if not os.path.exists(output_file):
            return {"message": "No crash data found"}
        
        try:
            # Read and parse text log file
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count crash entries
            crash_sections = content.split('CRASH DETECTED:')
            crashes = [section for section in crash_sections if section.strip()]
            
            if not crashes:
                return {"message": "No crashes recorded"}
            
            # Analyze crash data
            crash_types: Dict[str, int] = {}
            recent_crashes: List[str] = []
            
            now = datetime.now()
            for crash in crashes:
                # Extract crash type from text
                if 'Crash Type:' in crash:
                    type_line = [line for line in crash.split('\n') if 'Crash Type:' in line]
                    if type_line:
                        crash_type = type_line[0].split('Crash Type:')[1].strip()
                        crash_types[crash_type] = crash_types.get(crash_type, 0) + 1
                
                # Check if crash is recent (last 7 days)
                if crash.strip():
                    try:
                        # Extract timestamp from first line
                        first_line = crash.split('\n')[0].strip()
                        crash_time = datetime.fromisoformat(first_line)
                        if (now - crash_time).days <= 7:
                            recent_crashes.append(crash)
                    except:
                        pass  # Skip if timestamp parsing fails
            
            report: Dict[str, Any] = {
                "total_crashes": len(crashes),
                "recent_crashes_7_days": len(recent_crashes),
                "crash_types": crash_types,
                "log_file_size": f"{os.path.getsize(output_file) / 1024:.1f} KB",
                "analysis": {
                    "crash_frequency": len(recent_crashes) / 7,  # crashes per day
                    "common_crash_type": max(crash_types.items(), key=lambda x: x[1])[0] if crash_types else None
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return {"error": str(e)}

def main():
    """Main function to run the crash monitor."""
    monitor = EveOnlineCrashMonitor()
    
    try:
        print("Eve Online Crash Monitor")
        print("========================")
        print("Commands:")
        print("  start   - Start monitoring")
        print("  stop    - Stop monitoring")
        print("  report  - Generate crash report")
        print("  status  - Show current status")
        print("  quit    - Exit program")
        print()
        
        monitoring_threads: List[Any] = []
        
        while True:
            try:
                command = input("Enter command: ").strip().lower()
                
                if command == "start":
                    monitoring_threads = monitor.start_monitoring()
                    print(f"Monitoring started with {len(monitoring_threads)} threads. Press Ctrl+C to stop or type 'stop'")
                
                elif command == "stop":
                    monitor.stop_monitoring()
                    monitoring_threads.clear()  # Clear the thread list
                    print("Monitoring stopped")
                
                elif command == "report":
                    report = monitor.generate_report()
                    print("\nCrash Report:")
                    print("=============")
                    for key, value in report.items():
                        if key == "analysis":
                            print(f"{key.replace('_', ' ').title()}:")
                            for sub_key, sub_value in value.items():
                                print(f"  {sub_key.replace('_', ' ').title()}: {sub_value}")
                        else:
                            print(f"{key.replace('_', ' ').title()}: {value}")
                
                elif command == "status":
                    status = "Running" if monitor.monitoring else "Stopped"
                    print(f"Monitor status: {status}")
                    if monitor.monitoring:
                        eve_procs = monitor.get_running_eve_processes()
                        print(f"Eve processes detected: {len(eve_procs)}")
                        for proc in eve_procs:
                            try:
                                print(f"  PID {proc.pid}: {proc.name()}")
                            except Exception:
                                print(f"  PID {proc.pid}: Unknown process")
                
                elif command in ["quit", "exit", "q"]:
                    if monitor.monitoring:
                        monitor.stop_monitoring()
                    print("Goodbye!")
                    break
                
                else:
                    print("Unknown command. Available: start, stop, report, status, quit")
                    
            except KeyboardInterrupt:
                print("\nStopping monitoring...")
                monitor.stop_monitoring()
                break
            except EOFError:
                break
                
    except Exception as e:
        print(f"Error: {e}")
        if monitor.monitoring:
            monitor.stop_monitoring()

if __name__ == "__main__":
    main()
