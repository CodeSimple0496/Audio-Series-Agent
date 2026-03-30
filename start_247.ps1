# Watchdog script for Audio Series Agent
# This script ensures the agent is always running.

# Detect the local virtual environment Python if it exists
$pythonPath = "python"
if (Test-Path "$PSScriptRoot\.venv\Scripts\python.exe") {
    $pythonPath = "$PSScriptRoot\.venv\Scripts\python.exe"
    Write-Host "Using Virtual Environment: $pythonPath"
}

$arguments = "-m streamlit run app.py"
$logFile = "agent_watchdog.log"

function Write-Log($message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $message"
    Write-Host $logEntry
    $logEntry | Out-File -FilePath $logFile -Append
}

Write-Log "Starting Audio Series Agent Watchdog..."

while ($true) {
    Write-Log "Launching Streamlit App..."
    
    # Start the process and wait for it to exit
    # Use -Wait to hold the loop until the app is closed/crashes
    $process = Start-Process -FilePath $pythonPath -ArgumentList $arguments -Wait -NoNewWindow -PassThru
    
    $exitCode = $process.ExitCode
    Write-Log "Streamlit App exited with code $exitCode. Restarting in 5 seconds..."
    
    Start-Sleep -Seconds 5
}
