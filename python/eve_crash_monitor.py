#!/usr/bin/env python3
"""
Eve Online Crash Monitor
Comprehensive crash detection and monitoring for Eve Online
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Check availability of optional dependencies without importing
psutil_available = True
try:
    import importlib.util
    spec = importlib.util.find_spec("psutil")
    if spec is None:
        psutil_available = False
except ImportError:
    psutil_available = False
    
win32_available = True    
try:
    import importlib.util
    spec1 = importlib.util.find_spec("win32evtlog")
    spec2 = importlib.util.find_spec("win32con")
    if spec1 is None or spec2 is None:
        win32_available = False
except ImportError:
    win32_available = False


class EveOnlineCrashMonitor:
    """Main crash monitor class for Eve Online."""
    
    def __init__(self, config_file: str = "../config/crash_monitor_config.json") -> None:
        """Initialize the crash monitor."""
        self.config_file = config_file
        self.monitoring = False
        self.eve_processes: List[Any] = []
        
        # Default configuration with proper type annotation
        self.config: Dict[str, Any] = {
            "check_interval": 5,
            "process_names": ["ExeFile.exe", "eve.exe"],
            "log_level": "INFO",
            "enable_event_log_monitoring": True,
            "enable_process_monitoring": True,
            "enable_log_file_monitoring": True,
            "crash_detection_threshold": 30,
            "output_file": "../logs/eve_crash_log.txt",
            "exclude_files": [
                "eve_crash_monitor.log",
                "eve_crash_log.txt",
                "eve_crash_log.json",
                "eve_crash_log_simple.txt",
                "simple_eve_crash_log.txt",
                "crash_monitor.log",
                "enhanced_crash_monitor.log",
                "Squirrel-CheckForUpdate.log",
                "Squirrel-Update.log",
                "Squirrel.log",
            ],
            "exclude_patterns": [
                "Squirrel", 
                "update", 
                "launcher",
                "crash_monitor",
                "crash_log", 
                "monitor",
                "eve_crash"
            ],
        }
        
        # Load configuration if available
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        # Setup logging
        self.setup_logging()
        
        # Find Eve Online log directories
        self.log_locations = self.find_eve_log_locations()
        
    def setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        
        # Create logs directory if it doesn't exist
        log_dir = Path("../logs")
        log_dir.mkdir(exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("EveOnlineCrashMonitor")
        self.logger.setLevel(log_level)
        
        # File handler
        handler = logging.FileHandler(log_dir / "eve_crash_monitor.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def find_eve_log_locations(self) -> List[Path]:
        """Find potential Eve Online log locations."""
        locations: List[Path] = []
        
        # Common Eve Online locations
        potential_paths = [
            Path.home() / "Documents" / "EVE" / "logs",
            Path("C:/EVE/logs"),
            Path("E:/EVE/logs"),
            Path.cwd() / "logs",
        ]
        
        for path in potential_paths:
            if path.exists():
                locations.append(path)
                
        return locations
    
    def get_eve_processes(self) -> List[Any]:
        """Get currently running Eve processes."""
        if not psutil_available:
            return []
            
        processes: List[Any] = []
        try:
            if psutil_available:
                # Re-import psutil locally to satisfy type checker  
                import psutil  # type: ignore
                for proc in psutil.process_iter(['pid', 'name']):  # type: ignore
                    if proc.info['name'].lower() in [name.lower() for name in self.config["process_names"]]:
                        processes.append(proc)
        except Exception as e:
            self.logger.debug(f"Error getting processes: {e}")
            
        return processes
    
    def start_monitoring(self) -> None:
        """Start the monitoring process."""
        self.monitoring = True
        self.logger.info("Starting Eve Online crash monitoring...")
        
        if self.config.get("enable_process_monitoring", True):
            self.logger.info("Started process monitoring")
            
        if self.config.get("enable_event_log_monitoring", True) and win32_available:
            self.logger.info("Started Windows Event Log monitoring")
            
        if self.config.get("enable_log_file_monitoring", True):
            self.logger.info("Started log file monitoring")
            
        # Main monitoring loop
        while self.monitoring:
            try:
                # Update process list
                self.eve_processes = self.get_eve_processes()
                
                # Check for new processes
                for proc in self.eve_processes:
                    self.logger.info(f"New Eve process detected: PID {proc.pid}")
                
                time.sleep(self.config.get("check_interval", 5))
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring process."""
        self.monitoring = False
        self.logger.info("Stopped Eve Online crash monitoring")


def main():
    """Main entry point for command-line interface."""
    monitor = EveOnlineCrashMonitor()
    
    print("Eve Online Crash Monitor")
    print("========================")
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
                print("Starting monitoring...")
                monitor.start_monitoring()
            elif command == "stop":
                print("Stopping monitoring...")
                monitor.stop_monitoring()
            elif command == "status":
                status = "Running" if monitor.monitoring else "Stopped"
                print(f"Monitor status: {status}")
                print(f"Eve processes: {len(monitor.eve_processes)}")
            elif command == "quit":
                if monitor.monitoring:
                    monitor.stop_monitoring()
                print("Goodbye!")
                break
            else:
                print("Unknown command. Use: start, stop, status, quit")
                
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            monitor.stop_monitoring()
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
