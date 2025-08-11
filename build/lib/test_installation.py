#!/usr/bin/env python3
"""
Installation Test for Eve Online Crash Monitor
Tests all components to ensure proper installation
"""

import sys
import os
import json
from pathlib import Path

# Add the python directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing Python imports...")
    
    try:
        from eve_crash_monitor import EveOnlineCrashMonitor
        # Verify class is importable by checking its name
        assert EveOnlineCrashMonitor.__name__ == "EveOnlineCrashMonitor"
        print("  ✅ eve_crash_monitor")
    except Exception as e:
        print(f"  ❌ eve_crash_monitor: {e}")
        return False
    
    try:
        from crash_monitor_gui import CrashMonitorGUI
        # Verify class is importable by checking its name
        assert CrashMonitorGUI.__name__ == "CrashMonitorGUI"
        print("  ✅ crash_monitor_gui")
    except Exception as e:
        print(f"  ❌ crash_monitor_gui: {e}")
        return False
    
    try:
        from enhanced_crash_monitor import EnhancedCrashMonitor
        # Verify class is importable by checking its name
        assert EnhancedCrashMonitor.__name__ == "EnhancedCrashMonitor"
        print("  ✅ enhanced_crash_monitor")
    except Exception as e:
        print(f"  ❌ enhanced_crash_monitor: {e}")
        return False
    
    try:
        from eveloglite_client import LogLiteClient
        # Verify class is importable by checking its name
        assert LogLiteClient.__name__ == "LogLiteClient"
        print("  ✅ eveloglite_client")
    except Exception as e:
        print(f"  ❌ eveloglite_client: {e}")
        return False
    
    try:
        from run_monitor_auto import main as auto_main
        # Verify function is importable by checking it's callable
        assert callable(auto_main)
        print("  ✅ run_monitor_auto")
    except Exception as e:
        print(f"  ❌ run_monitor_auto: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that all required dependencies are available."""
    print("Testing dependencies...")
    
    try:
        import psutil
        # Verify psutil is working by checking its version
        version = getattr(psutil, '__version__', 'unknown')
        print(f"  ✅ psutil {version}")
    except Exception as e:
        print(f"  ❌ psutil: {e}")
        return False
    
    try:
        import win32evtlog
        # Verify win32evtlog is working by checking it has expected attributes
        assert hasattr(win32evtlog, 'OpenEventLog')
        print("  ✅ pywin32 (win32evtlog)")
    except Exception as e:
        print(f"  ⚠️ pywin32: {e} (optional)")
    
    try:
        import tkinter
        # Verify tkinter is working by checking it has Tk class
        assert hasattr(tkinter, 'Tk')
        print("  ✅ tkinter (GUI support)")
    except Exception as e:
        print(f"  ❌ tkinter: {e}")
        return False
    
    return True

def test_configuration():
    """Test that configuration files are accessible."""
    print("Testing configuration...")
    
    # Try multiple possible paths for the config file
    possible_paths = [
        Path("../config/crash_monitor_config.json"),
        Path("config/crash_monitor_config.json"),
        Path("../../config/crash_monitor_config.json")
    ]
    
    config_path = None
    for path in possible_paths:
        if path.exists():
            config_path = path
            break
    
    if not config_path:
        print(f"  ❌ Configuration file not found in any of: {[str(p) for p in possible_paths]}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"  ✅ Configuration file readable: {config_path}")
        
        # Check required config keys
        required_keys = ["check_interval", "process_names", "log_level"]
        for key in required_keys:
            if key in config:
                print(f"    ✅ {key}: {config[key]}")
            else:
                print(f"    ❌ Missing config key: {key}")
                return False
        
    except Exception as e:
        print(f"  ❌ Configuration file error: {e}")
        return False
    
    return True

def test_directories():
    """Test that required directories exist or can be created."""
    print("Testing directories...")
    
    # Try multiple possible paths for directories
    possible_logs_dirs = [
        Path("../logs"),
        Path("logs"),
        Path("../../logs")
    ]
    
    possible_config_dirs = [
        Path("../config"),
        Path("config"),
        Path("../../config")
    ]
    
    # Check logs directory
    logs_dir = None
    for path in possible_logs_dirs:
        if path.exists():
            logs_dir = path
            break
    
    if logs_dir:
        print(f"  ✅ Logs directory exists: {logs_dir}")
    else:
        try:
            # Create in the most likely location
            logs_dir = possible_logs_dirs[0]
            logs_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Logs directory created: {logs_dir}")
        except Exception as e:
            print(f"  ❌ Cannot create logs directory: {e}")
            return False
    
    # Check config directory
    config_dir = None
    for path in possible_config_dirs:
        if path.exists():
            config_dir = path
            break
    
    if config_dir:
        print(f"  ✅ Config directory exists: {config_dir}")
    else:
        print("  ❌ Config directory missing")
        return False
    
    return True

def test_monitor_functionality():
    """Test basic monitor functionality."""
    print("Testing monitor functionality...")
    
    try:
        from eve_crash_monitor import EveOnlineCrashMonitor
        monitor = EveOnlineCrashMonitor()
        print("  ✅ Monitor initialization")
        
        # Test process detection (should not error even if no Eve processes)
        processes = monitor.get_eve_processes()
        print(f"  ✅ Process detection ({len(processes)} processes found)")
        
        # Test log locations
        locations = monitor.find_eve_log_locations()
        print(f"  ✅ Log location detection ({len(locations)} locations found)")
        
    except Exception as e:
        print(f"  ❌ Monitor functionality: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("Eve Online Crash Monitor - Installation Test")
    print("=" * 50)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("Configuration", test_configuration),
        ("Directories", test_directories),
        ("Monitor Functionality", test_monitor_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"[{test_name}]")
        try:
            if test_func():
                print(f"  ✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"  ❌ {test_name} FAILED")
        except Exception as e:
            print(f"  ❌ {test_name} ERROR: {e}")
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Installation is successful!")
        return 0
    else:
        print("❌ Some tests failed - Installation needs attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
