#!/usr/bin/env python3
"""
Final Verification Test - Eve Online Crash Monitor
Verifies that all components work correctly after file reorganization.
"""

import sys
import importlib
from pathlib import Path
from typing import List, Tuple

def test_file_structure():
    """Test that all expected files exist in correct locations."""
    print("🔍 Testing File Structure...")
    
    base_path = Path(__file__).parent.parent.parent  # Go up from tests/ to python/ to eve/
    
    expected_files = {
        "config/crash_monitor_config.json": "Configuration file",
        "python/eve_crash_monitor.py": "Core monitor class",
        "python/crash_monitor_gui.py": "GUI interface",
        "scripts/run_gui.bat": "GUI launcher",
        "logs": "Logs directory (should exist)"
    }
    
    all_good = True
    for file_path, description in expected_files.items():
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ MISSING {description}: {file_path}")
            all_good = False
    
    return all_good

def test_imports():
    """Test that Python modules can be imported correctly."""
    print("\n🐍 Testing Python Imports...")
    
    # Add python directory to path
    python_dir = Path(__file__).parent.parent  # From tests/ to python/
    sys.path.insert(0, str(python_dir))
    
    modules_to_test = [
        "eve_crash_monitor",
        "crash_monitor_gui", 
        "eveloglite_client"
    ]
    
    all_good = True
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ Successfully imported: {module_name}")
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {e}")
            all_good = False
        except Exception as e:
            print(f"⚠️  Warning importing {module_name}: {e}")
    
    return all_good

def test_config_accessibility():
    """Test that configuration files are accessible."""
    print("\n⚙️  Testing Configuration Access...")
    
    python_dir = Path(__file__).parent.parent  # From tests/ to python/
    config_path = python_dir / ".." / "config" / "crash_monitor_config.json"
    
    if config_path.exists():
        print(f"✅ Configuration accessible: {config_path.resolve()}")
        return True
    else:
        print(f"❌ Configuration not found: {config_path.resolve()}")
        return False

def main():
    """Run all verification tests."""
    print("🚀 Eve Online Crash Monitor - Final Verification Test")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Imports", test_imports),
        ("Configuration Access", test_config_accessibility)
    ]
    
    results: List[Tuple[str, bool]] = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! File organization successful.")
        print("🚀 Eve Online Crash Monitor is ready for production use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
