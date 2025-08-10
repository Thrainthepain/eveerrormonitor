#!/usr/bin/env python3
"""
Test script to verify Eve Online Crash Monitor installation
"""

import sys
import os

def test_installation():
    """Test the installation of the crash monitor."""
    print("Testing Eve Online Crash Monitor Installation")
    print("=" * 50)
    
    # Test 1: Python version
    print(f"[OK] Python version: {sys.version}")
    
    # Test 2: Import dependencies
    try:
        import psutil
        print(f"[OK] psutil available (version: {psutil.__version__})")
    except ImportError:
        print("[ERROR] psutil not available")
        return False
    
    try:
        import win32evtlog
        # Test that we can actually use the module
        win32evtlog.GetNumberOfEventLogRecords
        print("[OK] pywin32 available")
    except ImportError:
        print("[ERROR] pywin32 not available")
        return False
    except AttributeError:
        print("[ERROR] pywin32 installation incomplete")
        return False
    
    # Test 3: Check if monitor script exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    monitor_path = os.path.join(script_dir, "eve_crash_monitor.py")
    if os.path.exists(monitor_path):
        print("[OK] Main monitor script found")
    else:
        print("[ERROR] Main monitor script not found")
        return False
    
    # Test 4: Check configuration
    config_path = os.path.join(script_dir, "crash_monitor_config.json")
    if os.path.exists(config_path):
        print("[OK] Configuration file found")
    else:
        print("[INFO] Configuration file not found (will be created on first run)")
    
    # Test 5: Check logs directory
    logs_dir = os.path.join(os.path.dirname(script_dir), "logs")
    if os.path.exists(logs_dir):
        print("[OK] Logs directory exists")
    else:
        print("[INFO] Logs directory not found (will be created on first run)")
    
    print()
    print("Installation test completed successfully!")
    print("You can now run the monitor with:")
    print("   scripts\\run_monitor.bat")
    print()
    
    return True

if __name__ == "__main__":
    try:
        test_installation()
    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        sys.exit(1)
