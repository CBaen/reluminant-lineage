# startup-services.ps1 - Master startup script for Wardenclyffe services
# Starts Ollama and warms up the embedding model
#
# This script is called from Windows Task Scheduler at logon

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Ollama if not already running
$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if (-not $ollamaProcess) {
    Write-Host "Starting Ollama..."
    Start-Process -FilePath "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

# Run warmup script
Write-Host "Running model warmup..."
& "$scriptDir\ollama-warmup.ps1"

Write-Host "Startup complete"
