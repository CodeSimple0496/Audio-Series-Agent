@echo off
:: Batch file to launch the PowerShell watchdog script
:: This ensures the Audio Series Agent stays running 24/7.

echo Initializing Audio Series Agent 24/7 Service...
powershell -ExecutionPolicy Bypass -File "%~dp0start_247.ps1"
pause
