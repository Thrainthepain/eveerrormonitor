# Log File Format Update Summary

## 📋 Changes Made

Updated all documentation to reflect that log files are now **text-based** instead of JSON format.

### ✅ Files Updated

#### 1. docs/POWERSHELL_README.md
- **Parameter description**: Changed from "JSON output file" to "Text output file"  
- **Default filename**: Changed from `eve_crash_log_ps.json` to `eve_crash_log_ps.txt`
- **Output description**: Updated to specify "text format" for crash logs

#### 2. docs/PYTHON_README.md  
- **Configuration example**: Changed `output_file` from `eve_crash_log.json` to `eve_crash_log.txt`
- **Output description**: Updated to specify "human-readable text format" for crash logs

### ✅ Already Correct
- **README.md**: Already correctly showed `.txt` files and "text-based logging"
- **Configuration files**: Correctly remain as `.json` (for settings, not logs)

## 🎯 Result

All documentation now consistently reflects the current text-based logging system:

- **Log outputs**: All crash logs are `.txt` files in human-readable format
- **Configuration**: Still uses `.json` for settings (which is correct)
- **Consistency**: All READMEs now match the actual file formats used

The documentation accurately describes the system as using **text-based logging** for easy analysis and review!
