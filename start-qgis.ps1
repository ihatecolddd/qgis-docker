$containerName = "qgis-enmap-container"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  QGIS Docker Environment with VNC" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if container is running
$containerStatus = docker inspect $containerName --format='{{.State.Running}}' 2>$null

if ($containerStatus -ne "true") {
    Write-Host "Starting container..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep 15
} else {
    Write-Host "Container already running" -ForegroundColor Green
}

Write-Host "`nStartup Logs:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
docker logs $containerName --tail 50

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "System Status:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
docker exec $containerName cat /config/system_status.json 2>$null | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Opening QGIS in Browser" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "URL: http://localhost:8888/vnc.html`n" -ForegroundColor Cyan

Start-Process "http://localhost:8888/vnc.html"

Write-Host "Commands:" -ForegroundColor Yellow
Write-Host "  View logs:   docker logs $containerName -f" -ForegroundColor White
Write-Host "  Stop:        docker-compose down" -ForegroundColor White
Write-Host "  Restart:     docker-compose restart`n" -ForegroundColor White