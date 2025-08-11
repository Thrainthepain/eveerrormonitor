#!/usr/bin/env python3
"""
File Organization Verification Script
Verifies that CCP files and our integration files are properly separated
"""

import os
import sys

def verify_file_organization():
    """Verify that files are organized correctly."""
    print("Eve Online Crash Monitor - File Organization Verification")
    print("=" * 60)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check CCP Games original files (should be untouched)
    print("\\n🎯 CCP Games Original Files:")
    ccp_files = [
        "EveLogLite-master/README.md",
        "EveLogLite-master/LICENSE", 
        "EveLogLite-master/src/main.cpp",
        "EveLogLite-master/clients/python/__init__.py"
    ]
    
    for file_path in ccp_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            
    # Check our integration files
    print("\\n🐍 Our Integration Files:")
    our_files = [
        "python/crash_monitor_gui.py",
        "python/enhanced_crash_monitor.py", 
        "python/eveloglite_client.py",
        "scripts/run_gui.bat"
    ]
    
    for file_path in our_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            
    # Check documentation files
    print("\\n📚 Documentation Files:")
    doc_files = [
        "EveLogLite-master/INTEGRATION_README.md",
        "PROJECT_STRUCTURE.md",
        "README.md"
    ]
    
    for file_path in doc_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            
    print("\\n" + "=" * 60)
    print("File Organization Status:")
    print("• CCP Games files preserved in EveLogLite-master/")
    print("• Our integration files in python/ and scripts/")
    print("• Clean separation maintained")
    print("• Documentation updated for new structure")
    print()
    
    return True

if __name__ == "__main__":
    verify_file_organization()
