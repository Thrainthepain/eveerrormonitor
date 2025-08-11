#!/usr/bin/env python3
"""
Enhanced Eve Online Crash Monitor with EveLogLite integration
Combines our crash monitoring with CCP's official log viewer
"""

import sys
import os
from typing import Optional, Any, Dict

# Add the python directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from eve_crash_monitor import EveOnlineCrashMonitor
    from eveloglite_client import LogLiteClient, Severity, log_crash
except ImportError as e:
    print(f"Error: Could not import required modules: {e}")
    sys.exit(1)


class EnhancedCrashMonitor(EveOnlineCrashMonitor):
    """Enhanced crash monitor with EveLogLite integration."""
    
    def __init__(self, use_loglite: bool = True, loglite_server: str = '127.0.0.1') -> None:
        super().__init__()
        self.use_loglite = use_loglite
        self.loglite_client: Optional[Any] = None
        
        if self.use_loglite:
            try:
                self.loglite_client = LogLiteClient(server=loglite_server)
                if self.loglite_client.connected:
                    print(f"✓ Connected to EveLogLite server at {loglite_server}")
                    self.log_to_loglite(Severity.INFO, "Crash monitor connected to EveLogLite")
                else:
                    print(f"⚠ Could not connect to EveLogLite server at {loglite_server}")
                    print("  Monitor will continue without EveLogLite integration")
            except Exception as e:
                print(f"⚠ EveLogLite connection failed: {e}")
                print("  Monitor will continue without EveLogLite integration")
                
    def log_to_loglite(self, severity: Any, message: str, module: str = 'CrashMonitor', channel: str = 'Events') -> None:
        """Send a log message to EveLogLite if connected."""
        if self.loglite_client and self.loglite_client.connected:
            try:
                self.loglite_client.log(severity, message, module=module, channel=channel)
            except Exception as e:
                print(f"Warning: Failed to send log to EveLogLite: {e}")
                
    def log_crash_event(self, crash_type: str, process_name: str, details: str) -> None:
        """Log a crash event to both file and EveLogLite."""
        # Log to the monitor's logger (which handles file logging)
        self.logger.error(f"CRASH DETECTED: {crash_type} - Process: {process_name} - Details: {details}")
        
        # Also send to EveLogLite if connected
        if self.loglite_client and self.loglite_client.connected:
            try:
                log_crash(self.loglite_client, crash_type, process_name, details)
                
                # Send additional context to different channels
                self.log_to_loglite(Severity.WARNING, 
                                  f"Process terminated: {process_name}", 
                                  module='ProcessMonitor', channel='Processes')
                                  
                self.log_to_loglite(Severity.ERROR, 
                                  f"Crash detected: {crash_type}", 
                                  module='CrashDetector', channel='Crashes')
            except Exception as e:
                print(f"Warning: Failed to log crash to EveLogLite: {e}")
                
    def start_monitoring(self):
        """Start monitoring with EveLogLite status updates."""
        if self.loglite_client and self.loglite_client.connected:
            self.log_to_loglite(Severity.INFO, "Starting crash monitoring", 
                              module='Monitor', channel='Status')
        
        super().start_monitoring()
        
    def stop_monitoring(self):
        """Stop monitoring with cleanup."""
        if self.loglite_client and self.loglite_client.connected:
            self.log_to_loglite(Severity.INFO, "Stopping crash monitoring", 
                              module='Monitor', channel='Status')
            self.loglite_client.close()
            
        super().stop_monitoring()


def main():
    """Main entry point for enhanced crash monitor."""
    print("Eve Online Enhanced Crash Monitor")
    print("=" * 40)
    print("Features:")
    print("• Advanced crash detection")
    print("• Real-time process monitoring")
    print("• Windows event log integration")
    print("• EveLogLite GUI integration (if available)")
    print()
    
    # Check for EveLogLite server
    use_loglite = True
    loglite_server = '127.0.0.1'
    
    # Initialize enhanced monitor
    try:
        monitor = EnhancedCrashMonitor(use_loglite=use_loglite, loglite_server=loglite_server)
    except Exception as e:
        print(f"Error initializing monitor: {e}")
        return 1
        
    # Interactive command loop
    print("Commands:")
    print("  start   - Start monitoring")
    print("  stop    - Stop monitoring")
    print("  status  - Show current status")
    print("  report  - Generate crash report")
    print("  test    - Send test message to EveLogLite")
    print("  quit    - Exit program")
    print()
    
    try:
        while True:
            try:
                command = input("Enter command: ").strip().lower()
                
                if command == "start":
                    print("Starting monitoring...")
                    monitor.start_monitoring()
                    print("✓ Monitoring started")
                    
                elif command == "stop":
                    print("Stopping monitoring...")
                    monitor.stop_monitoring()
                    print("✓ Monitoring stopped")
                    
                elif command == "status":
                    # Get status information directly from monitor attributes
                    eve_processes = getattr(monitor, 'eve_processes', [])
                    status: Dict[str, Any] = {
                        'monitoring': monitor.monitoring,
                        'eve_processes_detected': len(eve_processes),
                        'total_processes': len(eve_processes)
                    }
                    print(f"Monitoring: {status['monitoring']}")
                    print(f"Eve processes detected: {status['eve_processes_detected']}")
                    print(f"Total processes: {status['total_processes']}")
                    if monitor.loglite_client:
                        print(f"EveLogLite connected: {monitor.loglite_client.connected}")
                        
                elif command == "report":
                    # Generate a simple crash report from available data
                    eve_processes = getattr(monitor, 'eve_processes', [])
                    report = f"""Crash Monitor Report
==================
Monitoring Status: {monitor.monitoring}
Eve Processes: {len(eve_processes)}
Configuration: {monitor.config.get('process_names', [])}
"""
                    print("\\n" + str(report))
                    
                elif command == "test":
                    if monitor.loglite_client and monitor.loglite_client.connected:
                        monitor.log_to_loglite(Severity.INFO, "Test message from crash monitor", 
                                             module='Test', channel='Testing')
                        print("✓ Test message sent to EveLogLite")
                    else:
                        print("⚠ EveLogLite not connected")
                        
                elif command == "quit":
                    print("Stopping monitoring...")
                    monitor.stop_monitoring()
                    print("Goodbye!")
                    break
                    
                else:
                    print("Unknown command. Available: start, stop, status, report, test, quit")
                    
            except KeyboardInterrupt:
                print("\\n\\nStopping monitoring...")
                monitor.stop_monitoring()
                break
                
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
