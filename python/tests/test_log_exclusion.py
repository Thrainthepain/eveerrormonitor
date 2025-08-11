#!/usr/bin/env python3
"""
Test script to verify log exclusion is working properly
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from eve_crash_monitor import EveOnlineCrashMonitor
import logging

def test_exclusions():
    """Test that our own log files are properly excluded."""
    print("Testing log file exclusions...")
    
    # Create monitor with debug logging
    monitor = EveOnlineCrashMonitor()
    monitor.logger.setLevel(logging.DEBUG)
    
    # Add console handler to see debug messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    monitor.logger.addHandler(console_handler)
    
    # Get the exclusion configuration
    exclude_files = monitor.config.get("exclude_files", [
        "eve_crash_monitor.log",
        "eve_crash_log.txt",
        "eve_crash_log.json", 
        "eve_crash_log_simple.txt",
        "crash_monitor.log",
        "enhanced_crash_monitor.log",
        "Squirrel-CheckForUpdate.log",
        "Squirrel-Update.log",
        "Squirrel.log",
    ])
    
    exclude_patterns = monitor.config.get("exclude_patterns", [
        "Squirrel", 
        "update", 
        "launcher", 
        "crash_monitor",
        "crash_log",
        "monitor",
        "eve_crash"
    ])
    
    print(f"Exclude files: {exclude_files}")
    print(f"Exclude patterns: {exclude_patterns}")
    
    # Check logs directory
    logs_dir = Path("../logs")
    if logs_dir.exists():
        print(f"\nChecking files in {logs_dir}:")
        for log_file in logs_dir.glob("*.log"):
            should_exclude = False
            reason = ""
            
            # Check exact filename matches
            if log_file.name in exclude_files:
                should_exclude = True
                reason = f"exact filename match"
            
            # Check pattern matches
            if not should_exclude:
                for pattern in exclude_patterns:
                    if pattern.lower() in log_file.name.lower():
                        should_exclude = True
                        reason = f"pattern match: '{pattern}'"
                        break
            
            status = "EXCLUDED" if should_exclude else "MONITORED"
            print(f"  {log_file.name} -> {status} ({reason if should_exclude else 'no exclusion rule'})")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_exclusions()
