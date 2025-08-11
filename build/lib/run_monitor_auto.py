#!/usr/bin/env python3
"""
Non-interactive runner for Eve Online Crash Monitor
Starts monitoring automatically without user interaction
"""

import sys
import os
import signal
from typing import Any

# Add the python directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from eve_crash_monitor import EveOnlineCrashMonitor


def signal_handler(signum: int, frame: Any) -> None:
    """Handle Ctrl+C gracefully."""
    print("\n\nReceived interrupt signal. Stopping monitoring...")
    global monitor
    if monitor:
        monitor.stop_monitoring()
    print("Monitor stopped. Goodbye!")
    sys.exit(0)


def main():
    """Non-interactive main entry point."""
    global monitor
    
    print("Eve Online Crash Monitor - Non-Interactive Mode")
    print("=" * 50)
    print("Starting automatic monitoring...")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start monitor
    monitor = EveOnlineCrashMonitor()
    
    try:
        print("🚀 Starting crash monitoring...")
        print("Monitoring Eve Online processes for crashes...")
        print("This will run continuously until stopped with Ctrl+C")
        print()
        
        # Start monitoring (this will run indefinitely)
        monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user.")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        print(f"Error: {e}")
        if monitor:
            monitor.stop_monitoring()
        sys.exit(1)


if __name__ == "__main__":
    main()
