# ollama-warmup.ps1 - Pre-load embedding model on startup
# Run after Ollama starts to eliminate cold-start delay

# Wait for Ollama to be ready
$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "Ollama is ready"
        break
    } catch {
        $attempt++
        Start-Sleep -Seconds 2
    }
}

if ($attempt -eq $maxAttempts) {
    Write-Host "Ollama did not start in time"
    exit 1
}

# Warm up the embedding model
Write-Host "Warming up nomic-embed-text model..."
try {
    $body = @{
        model = "nomic-embed-text"
        prompt = "warmup embedding"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/embeddings" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
    Write-Host "Model warmed up successfully"
} catch {
    Write-Host "Warmup failed: $_"
}
