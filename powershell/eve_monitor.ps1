# Eve Online Crash Monitor - PowerShell Edition
# A PowerShell-based crash monitor for Eve Online

param(
    [string]$Action = "interactive",
    [int]$CheckInterval = 5,
    [int]$CrashThreshold = 30,
    [string]$OutputFile = "../logs/eve_crash_log_ps.json"
)

# Configuration
$ProcessNames = @("ExeFile.exe", "eve.exe", "EVE.exe")
$Script:Monitoring = $false
$Script:TrackedProcesses = @{}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path "../logs/eve_monitor_ps.log" -Value $logMessage
}

function Get-EveProcesses {
    $processes = @()
    foreach ($processName in $ProcessNames) {
        try {
            $procs = Get-Process -Name ($processName -replace '\.exe$', '') -ErrorAction SilentlyContinue
            foreach ($proc in $procs) {
                $processes += @{
                    Name = $proc.ProcessName + ".exe"
                    Id = $proc.Id
                    StartTime = $proc.StartTime
                    WorkingSet = $proc.WorkingSet64
                    Handle = $proc.Handle
                }
            }
        }
        catch {
            # Process not found, continue
        }
    }
    return $processes
}

function Test-ProcessExists {
    param([int]$ProcessId)
    try {
        $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        return $null -ne $proc
    }
    catch {
        return $false
    }
}

function Add-CrashEvent {
    param([hashtable]$CrashData)
    
    try {
        $data = @{
            crashes = @()
            summary = @{
                total_crashes = 0
                last_updated = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffK")
            }
        }
        
        if (Test-Path $OutputFile) {
            $existing = Get-Content $OutputFile -Raw | ConvertFrom-Json
            $data.crashes = @($existing.crashes)
        }
        
        $data.crashes += $CrashData
        $data.summary.total_crashes = $data.crashes.Count
        $data.summary.last_updated = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffK")
        
        # Keep only last 500 entries
        if ($data.crashes.Count -gt 500) {
            $data.crashes = $data.crashes[-500..-1]
            $data.summary.total_crashes = $data.crashes.Count
        }
        
        $data | ConvertTo-Json -Depth 10 | Set-Content $OutputFile
    }
    catch {
        Write-Log "Error logging crash event: $_" "ERROR"
    }
}

function Start-Monitoring {
    if ($Script:Monitoring) {
        Write-Log "Monitoring is already running" "WARNING"
        return
    }
    
    $Script:Monitoring = $true
    Write-Log "Starting Eve Online crash monitoring..."
    
    while ($Script:Monitoring) {
        try {
            $currentProcesses = Get-EveProcesses
            $currentIds = $currentProcesses | ForEach-Object { $_.Id }
            
            # Check for new processes
            foreach ($proc in $currentProcesses) {
                if (-not $Script:TrackedProcesses.ContainsKey($proc.Id)) {
                    $Script:TrackedProcesses[$proc.Id] = @{
                        Name = $proc.Name
                        StartTime = Get-Date
                        LastSeen = Get-Date
                        WorkingSet = $proc.WorkingSet
                        ProcessStartTime = $proc.StartTime
                    }
                    Write-Log "New Eve process detected: $($proc.Name) (PID $($proc.Id))"
                }
            }
            
            # Check for terminated processes
            $terminatedIds = $Script:TrackedProcesses.Keys | Where-Object { $_ -notin $currentIds }
            foreach ($processId in $terminatedIds) {
                if (-not (Test-ProcessExists $processId)) {
                    $processInfo = $Script:TrackedProcesses[$processId]
                    $runtime = (Get-Date) - $processInfo.StartTime
                    
                    $crashData = @{
                        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffK")
                        type = "process_termination"
                        pid = $processId
                        process_name = $processInfo.Name
                        runtime_seconds = $runtime.TotalSeconds
                        start_time = $processInfo.StartTime.ToString("yyyy-MM-ddTHH:mm:ss.fffK")
                        end_time = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffK")
                        memory_usage_mb = [math]::Round($processInfo.WorkingSet / 1MB, 1)
                        suspected_crash = $runtime.TotalSeconds -lt $CrashThreshold
                    }
                    
                    Add-CrashEvent $crashData
                    
                    if ($crashData.suspected_crash) {
                        Write-Log "POTENTIAL CRASH: $($processInfo.Name) (PID $processId) terminated after $([math]::Round($runtime.TotalSeconds, 1)) seconds" "WARNING"
                    }
                    else {
                        Write-Log "Normal termination: $($processInfo.Name) (PID $processId) ran for $([math]::Round($runtime.TotalSeconds, 1)) seconds"
                    }
                    
                    $Script:TrackedProcesses.Remove($processId)
                }
            }
            
            # Update existing processes
            foreach ($proc in $currentProcesses) {
                if ($Script:TrackedProcesses.ContainsKey($proc.Id)) {
                    $Script:TrackedProcesses[$proc.Id].LastSeen = Get-Date
                    $Script:TrackedProcesses[$proc.Id].WorkingSet = $proc.WorkingSet
                }
            }
            
            Start-Sleep $CheckInterval
        }
        catch {
            Write-Log "Error in monitoring loop: $_" "ERROR"
            Start-Sleep 5
        }
    }
}

function Stop-Monitoring {
    $Script:Monitoring = $false
    Write-Log "Monitoring stopped"
}

function Get-MonitorStatus {
    $currentProcesses = Get-EveProcesses
    
    $status = @{
        monitoring = $Script:Monitoring
        eve_processes_detected = $currentProcesses.Count
        tracked_processes = $Script:TrackedProcesses.Count
        current_processes = $currentProcesses
    }
    
    return $status
}

function Get-CrashReport {
    if (-not (Test-Path $OutputFile)) {
        return @{
            message = "No crash data found"
            total_events = 0
        }
    }
    
    try {
        $data = Get-Content $OutputFile -Raw | ConvertFrom-Json
        $crashes = @($data.crashes)
        
        if ($crashes.Count -eq 0) {
            return @{
                message = "No crashes recorded"
                total_events = 0
            }
        }
        
        $now = Get-Date
        $recentCrashes = @()
        $crashTypes = @{}
        $suspectedCrashes = 0
        
        foreach ($crash in $crashes) {
            $crashType = $crash.type
            if ($crashTypes.ContainsKey($crashType)) {
                $crashTypes[$crashType]++
            } else {
                $crashTypes[$crashType] = 1
            }
            
            if ($crash.suspected_crash) {
                $suspectedCrashes++
            }
            
            try {
                $crashTime = [DateTime]::Parse($crash.timestamp)
                if (($now - $crashTime).Days -le 7) {
                    $recentCrashes += $crash
                }
            }
            catch {
                # Skip invalid timestamp
            }
        }
        
        $report = @{
            total_events = $crashes.Count
            suspected_crashes = $suspectedCrashes
            recent_events_7_days = $recentCrashes.Count
            event_types = $crashTypes
            most_recent_event = $crashes[-1]
            analysis = @{
                crash_rate_per_day = [math]::Round($recentCrashes.Count / 7, 2)
                suspected_crash_percentage = if ($crashes.Count -gt 0) { [math]::Round(($suspectedCrashes / $crashes.Count) * 100, 1) } else { 0 }
            }
        }
        
        return $report
    }
    catch {
        return @{
            error = $_.Exception.Message
        }
    }
}

function Show-InteractiveMenu {
    Write-Host "Eve Online Crash Monitor - PowerShell Edition" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "Commands:"
    Write-Host "  start   - Start monitoring"
    Write-Host "  stop    - Stop monitoring"
    Write-Host "  status  - Show current status"
    Write-Host "  report  - Generate crash report"
    Write-Host "  quit    - Exit program"
    Write-Host ""
    
    while ($true) {
        $command = Read-Host "Enter command"
        
        switch ($command.ToLower()) {
            "start" {
                Start-Job -ScriptBlock { 
                    param($script, $interval, $threshold, $output)
                    & $script -Action "monitor" -CheckInterval $interval -CrashThreshold $threshold -OutputFile $output
                } -ArgumentList $PSCommandPath, $CheckInterval, $CrashThreshold, $OutputFile | Out-Null
                Write-Host "Monitoring started in background job." -ForegroundColor Green
                Write-Host "Use 'Get-Job' to check status, 'Stop-Job' to stop." -ForegroundColor Yellow
            }
            
            "stop" {
                Get-Job | Where-Object { $_.Command -like "*eve*monitor*" } | Stop-Job
                Get-Job | Where-Object { $_.Command -like "*eve*monitor*" } | Remove-Job
                Write-Host "Monitoring stopped." -ForegroundColor Red
            }
            
            "status" {
                $status = Get-MonitorStatus
                Write-Host "`nMonitor Status:" -ForegroundColor Yellow
                Write-Host "Eve processes detected: $($status.eve_processes_detected)"
                
                if ($status.current_processes.Count -gt 0) {
                    Write-Host "`nCurrent Eve processes:" -ForegroundColor Green
                    foreach ($proc in $status.current_processes) {
                        $memoryMB = [math]::Round($proc.WorkingSet / 1MB, 1)
                        Write-Host "  $($proc.Name) (PID $($proc.Id)) - $memoryMB MB"
                    }
                } else {
                    Write-Host "No Eve processes currently running." -ForegroundColor Gray
                }
                
                $jobs = Get-Job | Where-Object { $_.Command -like "*eve*monitor*" }
                Write-Host "`nMonitoring jobs: $($jobs.Count)"
                if ($jobs.Count -gt 0) {
                    $jobs | Format-Table Id, State, HasMoreData
                }
            }
            
            "report" {
                $report = Get-CrashReport
                Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
                Write-Host "EVE ONLINE CRASH ANALYSIS REPORT" -ForegroundColor Cyan
                Write-Host ("=" * 50) -ForegroundColor Cyan
                
                if ($report.ContainsKey("error")) {
                    Write-Host "Error: $($report.error)" -ForegroundColor Red
                } elseif ($report.total_events -eq 0) {
                    Write-Host $report.message -ForegroundColor Yellow
                } else {
                    Write-Host "Total Events: $($report.total_events)"
                    Write-Host "Suspected Crashes: $($report.suspected_crashes)"
                    Write-Host "Recent Events (7 days): $($report.recent_events_7_days)"
                    Write-Host "Crash Rate: $($report.analysis.crash_rate_per_day) events/day"
                    Write-Host "Suspected Crash Rate: $($report.analysis.suspected_crash_percentage)%"
                    
                    if ($report.most_recent_event) {
                        Write-Host "`nMost Recent Event: $($report.most_recent_event.timestamp)" -ForegroundColor Yellow
                        Write-Host "Type: $($report.most_recent_event.type)"
                        if ($report.most_recent_event.suspected_crash) {
                            Write-Host "⚠️  This was flagged as a suspected crash" -ForegroundColor Red
                        }
                    }
                }
                Write-Host ("=" * 50) -ForegroundColor Cyan
            }
            
            { $_ -in @("quit", "exit", "q") } {
                Write-Host "Stopping any running monitoring jobs..." -ForegroundColor Yellow
                Get-Job | Where-Object { $_.Command -like "*eve*monitor*" } | Stop-Job
                Get-Job | Where-Object { $_.Command -like "*eve*monitor*" } | Remove-Job
                Write-Host "Goodbye!" -ForegroundColor Green
                return
            }
            
            default {
                Write-Host "Unknown command. Available: start, stop, status, report, quit" -ForegroundColor Red
            }
        }
    }
}

# Main execution
switch ($Action) {
    "monitor" {
        Start-Monitoring
    }
    "interactive" {
        Show-InteractiveMenu
    }
    "status" {
        $status = Get-MonitorStatus
        $status | ConvertTo-Json -Depth 5
    }
    "report" {
        $report = Get-CrashReport
        $report | ConvertTo-Json -Depth 5
    }
    default {
        Write-Host "Usage: $($MyInvocation.MyCommand.Name) [-Action interactive|monitor|status|report]"
        Write-Host "  interactive (default) - Run interactive mode"
        Write-Host "  monitor               - Start monitoring (background)"
        Write-Host "  status                - Get current status"
        Write-Host "  report                - Generate crash report"
    }
}
