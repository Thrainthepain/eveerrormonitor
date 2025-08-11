#!/usr/bin/env python3
"""
Debug script to check what get_eve_processes returns
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from eve_crash_monitor import EveOnlineCrashMonitor

def debug_eve_processes():
    """Debug the get_eve_processes method."""
    print("Testing get_eve_processes method...")
    
    # Create monitor
    monitor = EveOnlineCrashMonitor()
    
    # Test the method
    try:
        processes = monitor.get_eve_processes()
        print(f"Type: {type(processes)}")
        print(f"Value: {processes}")
        print(f"Length: {len(processes) if processes else 'N/A'}")
        
        if processes:
            print("Process details:")
            for i, proc in enumerate(processes):
                print(f"  Process {i}: {proc} (type: {type(proc)})")
    except Exception as e:
        print(f"Error calling get_eve_processes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_eve_processes()
