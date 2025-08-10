#!/usr/bin/env python3
"""
Eve Online Simple Crash Monitor
A lightweight tool to detect Eve Online crashes using basic process monitoring.
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class SimpleEveMonitor:
    def __init__(self, config_file: str = "simple_monitor_config.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = self.load_config()
        self.setup_logging()
        self.eve_processes: Dict[str, Dict[str, Any]] = {}
        self.monitoring = False
        
    def get_logs_directory(self) -> str:
        """Get the absolute path to the logs directory."""
        # Get the script directory (where this file is located)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the project root and then to logs
        project_root = os.path.dirname(script_dir)
        logs_dir = os.path.join(project_root, "logs")
        
        # Create logs directory if it doesn't exist
        os.makedirs(logs_dir, exist_ok=True)
        
        return logs_dir
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default config."""
        # Get the logs directory path using a simple calculation
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        logs_dir = os.path.join(project_root, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        default_output_file = os.path.join(logs_dir, "eve_crash_log_simple.txt")
        
        default_config: Dict[str, Any] = {
            "check_interval": 5,
            "process_names": ["ExeFile.exe", "eve.exe"],
            "log_level": "INFO",
            "enable_process_monitoring": True,
            "enable_system_monitoring": True,
            "crash_detection_threshold": 30,
            "output_file": default_output_file
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
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
        log_level_str: str = self.config.get("log_level", "INFO")
        log_level = getattr(logging, log_level_str)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('simple_eve_monitor.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_processes_via_tasklist(self) -> List[Dict[str, Any]]:
        """Get running processes using Windows tasklist command."""
        processes: List[Dict[str, Any]] = []
        process_names: List[str] = self.config.get("process_names", ["ExeFile.exe", "eve.exe"])
        
        try:
            for process_name in process_names:
                # Use tasklist to get detailed process information
                cmd = [
                    "tasklist", "/FI", f"IMAGENAME eq {process_name}",
                    "/FO", "CSV", "/V"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:  # Skip header line
                        for line in lines[1:]:
                            if line.strip():
                                # Parse CSV output
                                parts = [part.strip('"') for part in line.split('","')]
                                if len(parts) >= 5:
                                    process_info: Dict[str, Any] = {
                                        'name': parts[0],
                                        'pid': int(parts[1]) if parts[1].isdigit() else 0,
                                        'session_name': parts[2],
                                        'session_number': parts[3],
                                        'memory_usage': self.parse_memory_usage(parts[4]),
                                        'window_title': parts[8] if len(parts) > 8 else ""
                                    }
                                    processes.append(process_info)
        except Exception as e:
            self.logger.error(f"Error getting processes via tasklist: {e}")
        
        return processes
    
    def parse_memory_usage(self, memory_str: str) -> int:
        """Parse memory usage string and return bytes."""
        try:
            # Remove commas and 'K' suffix, convert to bytes
            memory_kb = int(memory_str.replace(',', '').replace(' K', ''))
            return memory_kb * 1024
        except Exception:
            return 0
    
    def check_process_still_running(self, pid: int) -> bool:
        """Check if a process is still running using tasklist."""
        try:
            cmd = ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                return len(lines) > 1  # More than just header means process exists
            return False
        except Exception:
            return False
    
    def get_process_details(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get detailed process information for a specific PID."""
        try:
            cmd = ["wmic", "process", "where", f"ProcessId={pid}", "get", 
                   "Name,ProcessId,CreationDate,WorkingSetSize,CommandLine", "/format:csv"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip() and str(pid) in line:
                        parts = line.split(',')
                        if len(parts) >= 6:
                            return {
                                'command_line': parts[1] if len(parts) > 1 else "",
                                'creation_date': parts[2] if len(parts) > 2 else "",
                                'name': parts[3] if len(parts) > 3 else "",
                                'pid': int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else pid,
                                'working_set_size': int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0
                            }
            return None
        except Exception as e:
            self.logger.debug(f"Error getting process details for PID {pid}: {e}")
            return None
    
    def monitor_processes(self):
        """Monitor Eve Online processes for unexpected termination."""
        while self.monitoring:
            try:
                current_processes = self.get_processes_via_tasklist()
                current_pids = {str(proc['pid']): proc for proc in current_processes if proc['pid'] > 0}
                
                # Check for new processes
                for pid_str, proc in current_pids.items():
                    if pid_str not in self.eve_processes:
                        details = self.get_process_details(proc['pid'])
                        if details:
                            self.eve_processes[pid_str] = details
                            self.eve_processes[pid_str]['start_time'] = datetime.now()
                            self.eve_processes[pid_str]['last_seen'] = datetime.now()
                            self.logger.info(f"New Eve process detected: PID {pid_str}")
                
                # Check for terminated processes
                terminated_pids = set(self.eve_processes.keys()) - set(current_pids.keys())
                for pid_str in terminated_pids:
                    process_info = self.eve_processes[pid_str]
                    start_time: datetime = process_info['start_time']
                    runtime = datetime.now() - start_time
                    
                    crash_data: Dict[str, Any] = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'process_termination',
                        'pid': pid_str,
                        'runtime_seconds': runtime.total_seconds(),
                        'start_time': start_time.isoformat(),
                        'end_time': datetime.now().isoformat(),
                        'memory_usage_mb': process_info.get('working_set_size', 0) / (1024 * 1024),
                        'suspected_crash': runtime.total_seconds() < self.config.get('crash_detection_threshold', 30)
                    }
                    
                    self.log_crash_event(crash_data)
                    
                    if crash_data['suspected_crash']:
                        self.logger.warning(f"Potential crash detected: Eve process {pid_str} terminated after {runtime.total_seconds():.1f} seconds")
                    else:
                        self.logger.info(f"Eve process {pid_str} terminated normally after {runtime.total_seconds():.1f} seconds")
                    
                    # Clean up terminated process
                    for proc in current_processes:
                        if str(proc['pid']) == pid_str:
                            crash_data.update({
                                'process_name': proc['name'],
                                'memory_usage_tasklist': proc['memory_usage']
                            })
                            break
                    
                    del self.eve_processes[pid_str]
                    
                # Update existing processes
                for pid_str in self.eve_processes:
                    if pid_str in current_pids:
                        self.eve_processes[pid_str]['last_seen'] = datetime.now()
                        proc = current_pids[pid_str]
                        memory_mb: float = proc['memory_usage'] / (1024 * 1024)
                        
                        # Check for high memory usage
                        memory_threshold: float = self.config.get('memory_warning_mb', 4000)
                        if memory_mb > memory_threshold:
                            self.logger.warning(f"High memory usage detected: PID {pid_str} using {memory_mb:.1f} MB")
                
                time.sleep(self.config.get("check_interval", 5))
                
            except Exception as e:
                self.logger.error(f"Error in process monitoring: {e}")
                time.sleep(5)
    
    def monitor_system_events(self):
        """Monitor system for crash-related events using basic Windows commands."""
        if not self.config.get("enable_system_monitoring", True):
            return
            
        while self.monitoring:
            try:
                # Check Windows Event Log for application errors
                cmd = [
                    "wevtutil", "qe", "Application", "/c:10", "/rd:true", "/f:text",
                    "/q:*[System[(EventID=1000 or EventID=1001) and TimeCreated[timediff(@SystemTime) <= 300000]]]"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.split('\n')
                    for i, line in enumerate(lines):
                        if 'eve' in line.lower() or 'exefile' in line.lower():
                            crash_data: Dict[str, Any] = {
                                'timestamp': datetime.now().isoformat(),
                                'type': 'system_event',
                                'source': 'Windows Event Log',
                                'description': line.strip(),
                                'context': lines[max(0, i-2):i+3]  # Include some context
                            }
                            self.log_crash_event(crash_data)
                            self.logger.warning(f"System event detected: {line.strip()}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring system events: {e}")
                time.sleep(30)
    
    def log_crash_event(self, crash_data: Dict[str, Any]):
        """Log crash event to output file."""
        output_file: str = self.config.get("output_file", os.path.join(self.get_logs_directory(), "eve_crash_log_simple.txt"))
        
        # Ensure the output file uses absolute path
        if not os.path.isabs(output_file):
            output_file = os.path.join(self.get_logs_directory(), os.path.basename(output_file))
        
        try:
            # Format crash data as human-readable text
            timestamp = crash_data.get("timestamp", datetime.now().isoformat())
            crash_type = crash_data.get("type", "Unknown")
            process_info = crash_data.get("process_info", {})
            system_info = crash_data.get("system_info", {})
            
            # Create formatted log entry
            log_entry = f"""
{'='*60}
CRASH DETECTED: {timestamp}
{'='*60}
Crash Type: {crash_type}
Process: {process_info.get('name', 'Unknown')} (PID: {process_info.get('pid', 'Unknown')})
Command Line: {process_info.get('cmd', 'Unknown')}

System Information:
- CPU Usage: {system_info.get('cpu_percent', 'Unknown')}%
- Memory Usage: {system_info.get('memory_percent', 'Unknown')}%
- Available Memory: {system_info.get('available_memory_gb', 'Unknown')} GB

Details: {crash_data.get('details', 'No additional details')}
{'='*60}

"""
            
            # Append to log file
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            self.logger.error(f"Error logging crash event: {e}")
    
    def start_monitoring(self):
        """Start monitoring threads."""
        if self.monitoring:
            self.logger.warning("Monitoring is already running")
            return
        
        self.monitoring = True
        self.logger.info("Starting simple Eve Online crash monitoring...")
        
        if self.config.get("enable_process_monitoring", True):
            process_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            process_thread.start()
            self.logger.info("Started process monitoring")
        
        if self.config.get("enable_system_monitoring", True):
            system_thread = threading.Thread(target=self.monitor_system_events, daemon=True)
            system_thread.start()
            self.logger.info("Started system event monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False
        self.logger.info("Stopped simple Eve Online crash monitoring")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        current_processes = self.get_processes_via_tasklist()
        
        status: Dict[str, Any] = {
            "monitoring": self.monitoring,
            "total_processes": len(current_processes),
            "eve_processes": len(self.eve_processes),
            "config": self.config
        }
        
        return status
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a crash report from logged events."""
        output_file: str = self.config.get("output_file", "eve_crash_log_simple.txt")
        
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
                    type_lines = [line for line in crash.split('\n') if 'Crash Type:' in line]
                    if type_lines:
                        crash_type = type_lines[0].split('Crash Type:')[1].strip()
                        crash_types[crash_type] = crash_types.get(crash_type, 0) + 1
                
                # Check if crash is recent (last 7 days)
                if crash.strip():
                    try:
                        # Extract timestamp from first line
                        first_line = crash.split('\n')[0].strip()
                        crash_time = datetime.fromisoformat(first_line)
                        if (now - crash_time).days <= 7:
                            recent_crashes.append(crash)
                    except Exception:
                        continue
            
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

    def get_recommendations(self, crashes: List[Dict[str, Any]]) -> List[str]:
        """Get recommendations based on crash patterns."""
        recommendations: List[str] = []
        
        if not crashes:
            return ["No crashes detected - system appears stable"]
        
        # Analyze crash patterns
        crash_count = len(crashes)
        memory_crashes = sum(1 for crash in crashes if crash.get('memory_usage_mb', 0) > 3000)
        
        if crash_count > 5:
            recommendations.append("Multiple crashes detected - consider updating graphics drivers")
            recommendations.append("Check Windows Event Viewer for additional error details")
            recommendations.append("Verify Eve Online client integrity through launcher")
            recommendations.append("Consider running memory diagnostic tools")
            recommendations.append("Check for Windows updates and install if available")
        
        if memory_crashes > 2:
            recommendations.append("High memory usage crashes detected - close other applications while playing")
            recommendations.append("Consider increasing virtual memory/page file size")
            recommendations.append("Check for memory leaks in other running applications")
            recommendations.append("Monitor system memory usage during gameplay")
        
        # Check for recent frequent crashes
        now = datetime.now()
        recent_crashes = [c for c in crashes if 
                         datetime.fromisoformat(c.get('timestamp', '1970-01-01T00:00:00')) > now - timedelta(hours=24)]
        if len(recent_crashes) > 3:
            recommendations.append("Frequent recent crashes detected - restart computer before playing")
            recommendations.append("Check system temperature and ensure adequate cooling")
            recommendations.append("Temporarily disable game overlays (Discord, Steam, etc.)")
            recommendations.append("Run Eve in windowed mode to reduce graphics load")
        
        return recommendations if recommendations else ["System appears stable - no specific recommendations"]

def main():
    """Main function to run the simple crash monitor."""
    monitor = SimpleEveMonitor()
    
    try:
        print("Eve Online Simple Crash Monitor")
        print("===============================")
        print("Commands:")
        print("  start   - Start monitoring")
        print("  stop    - Stop monitoring")
        print("  report  - Generate crash report")
        print("  status  - Show current status")
        print("  quit    - Exit program")
        print()
        
        while True:
            try:
                command = input("Enter command: ").strip().lower()
                
                if command == "start":
                    monitor.start_monitoring()
                    print("Simple monitoring started. Press Ctrl+C to stop or type 'stop'")
                
                elif command == "stop":
                    monitor.stop_monitoring()
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
                    status = monitor.get_status()
                    print(f"Monitor status: {'Running' if status['monitoring'] else 'Stopped'}")
                    print(f"Total processes found: {status['total_processes']}")
                    print(f"Eve processes tracked: {status['eve_processes']}")
                    
                    if status['monitoring']:
                        current_procs = monitor.get_processes_via_tasklist()
                        for proc in current_procs:
                            if proc['pid'] > 0:
                                memory_mb: float = proc['memory_usage'] / (1024 * 1024)
                                print(f"  PID {proc['pid']}: {proc['name']} ({memory_mb:.1f} MB)")
                
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
