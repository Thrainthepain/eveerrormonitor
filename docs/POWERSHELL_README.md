# PowerShell Monitoring System

Real-time process monitoring using native PowerShell capabilities.

## Files

- **`eve_monitor.ps1`** - PowerShell-based crash monitor

## Usage

### Interactive Mode
```powershell
powershell -ExecutionPolicy Bypass -File "eve_monitor.ps1" -Action "interactive"
```

Commands within interactive mode:
- `start` - Start monitoring
- `stop` - Stop monitoring
- `status` - Show current status  
- `report` - Generate crash report
- `quit` - Exit program

### Background Job Mode
```powershell
# Start as background job
Start-Job -Name "EveMonitor" -ScriptBlock { 
    Set-Location "E:\eve\powershell"
    powershell -ExecutionPolicy Bypass -File ".\eve_monitor.ps1" -Action "monitor"
}

# Check job status
Get-Job -Name "EveMonitor"

# View job output
Receive-Job -Name "EveMonitor" -Keep

# Stop monitoring
Stop-Job -Name "EveMonitor"; Remove-Job -Name "EveMonitor"
```

### Direct Actions
```powershell
# Get status
.\eve_monitor.ps1 -Action "status"

# Generate report
.\eve_monitor.ps1 -Action "report"
```

## Features

- Process termination detection
- Memory usage monitoring
- Crash threshold analysis
- JSON logging
- Background job support

## Configuration

Parameters:
- `-CheckInterval` - Seconds between checks (default: 5)
- `-CrashThreshold` - Seconds to consider a crash (default: 30)
- `-OutputFile` - Text output file (default: "eve_crash_log_ps.txt")

## Output

Logs are saved to `../logs/` directory:
- `eve_monitor_ps.log` - Activity log
- `eve_crash_log_ps.txt` - Detected crashes in text format
