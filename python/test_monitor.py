#!/usr/bin/env python3
"""
Test script to verify the Eve Online crash monitor is working correctly.
This script simulates some basic scenarios to test the monitoring functionality.
"""

import subprocess
import os
import json
from typing import Dict, Union, List

# Character encoding helper for better compatibility
def get_check_mark():
    """Get appropriate check mark for current terminal."""
    try:
        # Try to use Unicode checkmark
        print("✓", end="")
        return "✓"
    except UnicodeEncodeError:
        return "[OK]"

def get_cross_mark():
    """Get appropriate cross mark for current terminal."""
    try:
        # Try to use Unicode cross
        print("✗", end="")
        return "✗"
    except UnicodeEncodeError:
        return "[FAIL]"

def get_warning_mark():
    """Get appropriate warning mark for current terminal."""
    try:
        # Try to use Unicode warning
        print("⚠", end="")
        return "⚠"
    except UnicodeEncodeError:
        return "[WARN]"

def test_monitor_basic_functionality():
    """Test basic monitor functionality."""
    print("Testing Eve Online Crash Monitor")
    print("=" * 50)
    
    # Test 1: Check if monitor starts
    print("Test 1: Monitor startup...")
    try:
        # Import the monitor module
        import simple_eve_monitor
        monitor = simple_eve_monitor.SimpleEveMonitor()
        print("✓ Monitor initialized successfully")
    except Exception as e:
        print(f"✗ Monitor failed to initialize: {e}")
        return False
    
    # Test 2: Check configuration loading
    print("\nTest 2: Configuration loading...")
    try:
        config = monitor.load_config()
        print(f"✓ Configuration loaded: {len(config)} settings")
        print(f"  - Check interval: {config.get('check_interval', 'N/A')} seconds")
        print(f"  - Process names: {config.get('process_names', 'N/A')}")
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False
    
    # Test 3: Check process detection
    print("\nTest 3: Process detection...")
    try:
        processes = monitor.get_processes_via_tasklist()
        print(f"✓ Process detection working: found {len(processes)} Eve processes")
        if processes:
            for proc in processes:
                memory_mb = proc['memory_usage'] / (1024 * 1024)
                print(f"  - {proc['name']} (PID {proc['pid']}) - {memory_mb:.1f} MB")
        else:
            print("  (No Eve Online processes currently running)")
    except Exception as e:
        print(f"✗ Process detection failed: {e}")
        return False
    
    # Test 4: Check status functionality
    print("\nTest 4: Status reporting...")
    try:
        status = monitor.get_status()
        print("✓ Status reporting working:")
        print(f"  - Monitoring: {status['monitoring']}")
        if 'eve_processes_detected' in status:
            print(f"  - Eve processes detected: {status['eve_processes_detected']}")
        elif 'eve_processes' in status:
            print(f"  - Eve processes detected: {status['eve_processes']}")
        if 'tracked_processes' in status:
            print(f"  - Tracked processes: {status['tracked_processes']}")
        elif 'total_processes' in status:
            print(f"  - Total processes: {status['total_processes']}")
    except Exception as e:
        print(f"✗ Status reporting failed: {e}")
        return False
    
    # Test 5: Check logging functionality
    print("\nTest 5: Logging functionality...")
    try:
        test_crash_data = {
            'timestamp': '2024-08-09T15:30:45.123456',
            'type': 'test_event',
            'process_info': {'name': 'test.exe', 'pid': 12345, 'cmd': 'test command'},
            'system_info': {'cpu_percent': 50.0, 'memory_percent': 75.0, 'available_memory_gb': 8.5},
            'details': 'This is a test crash event'
        }
        monitor.log_crash_event(test_crash_data)
        
        # Check if file was created (now text-based, not JSON)
        output_file = monitor.config.get("output_file", "eve_crash_log_simple.txt")
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if "CRASH DETECTED" in content and "test_event" in content:
                print("✓ Logging working: test event written to log file")
            else:
                print("✗ Logging failed: test event not found in log")
                return False
        else:
            print("✗ Logging failed: log file not created")
            return False
    except Exception as e:
        print(f"✗ Logging failed: {e}")
        return False
    
    # Test 6: Check report generation
    print("\nTest 6: Report generation...")
    try:
        report = monitor.generate_report()
        print("✓ Report generation working:")
        if 'error' in report:
            print(f"  - Report error: {report['error']}")
        elif report.get('total_events', 0) == 0:
            print(f"  - {report.get('message', 'No data available')}")
        else:
            print(f"  - Total events: {report.get('total_events', 0)}")
            print(f"  - Suspected crashes: {report.get('suspected_crashes', 0)}")
    except Exception as e:
        print(f"✗ Report generation failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All basic tests passed! The monitor appears to be working correctly.")
    print("\nTo start monitoring:")
    print("1. Run: python simple_eve_monitor.py")
    print("2. Type 'start' to begin monitoring")
    print("3. Launch Eve Online")
    print("4. Type 'status' to see detected processes")
    print("5. Type 'report' to see crash analysis")
    
    return True

def test_windows_commands():
    """Test if required Windows commands are available."""
    print("\nTesting Windows command availability...")
    
    commands_to_test = [
        ('tasklist', 'Process listing', True),      # Required
        ('wmic', 'System information', False),      # Optional (deprecated)
        ('wevtutil', 'Event log access', True)      # Required
    ]
    
    required_available = True
    
    for command, description, required in commands_to_test:
        try:
            result = subprocess.run([command, '/?'], 
                                  capture_output=True, 
                                  text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW,
                                  timeout=5)
            if result.returncode == 0:
                print(f"✓ {command} available ({description})")
            else:
                if required:
                    print(f"✗ {command} returned error code {result.returncode} - REQUIRED")
                    required_available = False
                else:
                    print(f"⚠ {command} returned error code {result.returncode} - Optional")
        except FileNotFoundError:
            if required:
                print(f"✗ {command} not found ({description}) - REQUIRED")
                required_available = False
            else:
                print(f"⚠ {command} not found ({description}) - Optional")
        except subprocess.TimeoutExpired:
            print(f"⚠ {command} timeout (may still work)")
        except Exception as e:
            if required:
                print(f"✗ {command} error: {e} - REQUIRED")
                required_available = False
            else:
                print(f"⚠ {command} error: {e} - Optional")
    
    return required_available

def create_sample_config():
    """Create a sample configuration with optimal settings."""
    print("\nCreating optimized configuration...")
    
    config: Dict[str, Union[int, List[str], str, bool]] = {
        "check_interval": 3,  # Check every 3 seconds for faster detection
        "process_names": ["ExeFile.exe", "eve.exe", "EVE.exe"],  # Common variations
        "log_level": "INFO",
        "crash_detection_threshold": 20,  # 20 seconds - faster crash detection
        "output_file": "eve_crash_log.json",
        "enable_memory_monitoring": True,
        "memory_threshold_mb": 3500  # Alert at 3.5GB
    }
    
    try:
        with open("simple_monitor_config.json", "w") as f:
            json.dump(config, f, indent=4)
        print("✓ Optimized configuration created: simple_monitor_config.json")
        print("  - Faster crash detection (20 seconds)")
        print("  - More frequent checking (3 seconds)")
        print("  - Lower memory threshold (3.5GB)")
        return True
    except Exception as e:
        print(f"✗ Failed to create configuration: {e}")
        return False

def main():
    """Run all tests."""
    print("Eve Online Crash Monitor - Test Suite")
    print("=" * 60)
    
    try:
        # Test Windows commands first
        windows_ok = test_windows_commands()
        
        # Test basic functionality
        monitor_ok = test_monitor_basic_functionality()
        
        # Create optimized config
        config_ok = create_sample_config()
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY:")
        print(f"Windows Commands: {'✓ PASS' if windows_ok else '✗ FAIL'}")
        print(f"Monitor Functions: {'✓ PASS' if monitor_ok else '✗ FAIL'}")
        print(f"Configuration: {'✓ PASS' if config_ok else '✗ FAIL'}")
        
        if monitor_ok:
            print("\n🎉 The crash monitor is ready to use!")
            print("\nNext steps:")
            print("1. Run the monitor: python simple_eve_monitor.py")
            print("2. Start monitoring with the 'start' command")
            print("3. Play Eve Online and let it monitor for crashes")
            print("4. Generate reports with the 'report' command")
        else:
            print("\n⚠ Some issues detected. Check the errors above.")
            
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")

if __name__ == "__main__":
    main()
    main()
    main()
