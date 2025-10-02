# start-qgis.ps1
$containerName = "qgis-enmap-container"  # Change this to your container name

Write-Host "Starting QGIS Environment..." -ForegroundColor Green

# Start container if not running
$containerStatus = docker inspect $containerName --format='{{.State.Running}}' 2>$null
if ($containerStatus -ne "true") {
    Write-Host "Starting container..." -ForegroundColor Yellow
    docker start $containerName
    Start-Sleep 5  # Give container more time to fully start
}

Write-Host "Cleaning up old processes..." -ForegroundColor Yellow
docker exec $containerName pkill -9 Xvfb x11vnc websockify fluxbox qgis 2>$null
docker exec $containerName rm -rf /tmp/.X* /tmp/runtime-root
Start-Sleep 2

Write-Host "Starting X server (Xvfb)..." -ForegroundColor Yellow
docker exec -d $containerName Xvfb :1 -screen 0 1280x1024x24 -ac
Start-Sleep 3

Write-Host "Starting window manager (Fluxbox)..." -ForegroundColor Yellow
docker exec -d $containerName sh -c "DISPLAY=:1 fluxbox"
Start-Sleep 3

Write-Host "Starting VNC server (x11vnc)..." -ForegroundColor Yellow
docker exec -d $containerName sh -c "DISPLAY=:1 x11vnc -display :1 -forever -nopw -listen localhost -rfbport 5900"
Start-Sleep 3

Write-Host "Starting web VNC (websockify)..." -ForegroundColor Yellow
docker exec -d $containerName sh -c "cd /usr/share/novnc && websockify --web=./ 8888 localhost:5900"
Start-Sleep 3

Write-Host "Starting QGIS..." -ForegroundColor Yellow
docker exec -d $containerName sh -c "DISPLAY=:1 LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none qgis --nologo"
Start-Sleep 2

# Verify services are running
Write-Host "`nVerifying services..." -ForegroundColor Cyan
$services = docker exec $containerName ps aux 2>$null
if ($services -match "Xvfb") { Write-Host "  ✓ Xvfb running" -ForegroundColor Green } else { Write-Host "  ✗ Xvfb NOT running" -ForegroundColor Red }
if ($services -match "x11vnc") { Write-Host "  ✓ x11vnc running" -ForegroundColor Green } else { Write-Host "  ✗ x11vnc NOT running" -ForegroundColor Red }
if ($services -match "websockify") { Write-Host "  ✓ websockify running" -ForegroundColor Green } else { Write-Host "  ✗ websockify NOT running" -ForegroundColor Red }
if ($services -match "qgis") { Write-Host "  ✓ QGIS running" -ForegroundColor Green } else { Write-Host "  ✗ QGIS NOT running" -ForegroundColor Red }

Write-Host "`nOpening QGIS in browser..." -ForegroundColor Green
Start-Process "http://localhost:8888/vnc.html"

Write-Host "`nQGIS is ready at: http://localhost:8888/vnc.html" -ForegroundColor Green
Write-Host "If connection fails, wait a few seconds and refresh the page" -ForegroundColor Yellow
