#!/bin/bash
set -e

LOG_FILE="/logs/startup.log"
STATUS_FILE="/config/system_status.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_section() {
    echo -e "\n${CYAN}========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}$1${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}========================================${NC}" | tee -a "$LOG_FILE"
}

# Initialize
echo "=== QGIS VNC Environment Startup ===" > "$LOG_FILE"
log_section "Step 1: Checking Python Packages"

# Check packages using Python
python3 << 'PYEOF' | tee -a "$LOG_FILE"
import sys
try:
    import importlib.metadata as metadata
    packages = ['numpy', 'scipy', 'pandas', 'matplotlib', 'dask', 'distributed', 
                'spectral', 'python-dotenv', 'pyqtgraph', 'pyyaml']
    
    print("\nPackage Status:")
    all_ok = True
    for pkg in packages:
        try:
            if pkg == 'python-dotenv':
                __import__('dotenv')
                ver = metadata.version('python-dotenv')
            elif pkg == 'pyyaml':
                __import__('yaml')
                ver = metadata.version('pyyaml')
            else:
                __import__(pkg)
                ver = metadata.version(pkg)
            print(f"  ✓ {pkg:20s} {ver}")
        except:
            print(f"  ✗ {pkg:20s} NOT FOUND")
            all_ok = False
    
    if not all_ok:
        sys.exit(1)
    print("\n✓ All packages installed")
    
    # Test Dask
    print("\nTesting Dask:")
    import dask.array as da
    x = da.ones((100, 100), chunks=(10, 10))
    result = x.sum().compute()
    print(f"  ✓ Dask test passed (sum={result})")
    
    # Check QGIS
    print("\nChecking QGIS:")
    from qgis.core import Qgis
    print(f"  ✓ QGIS {Qgis.version()}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    log_error "Package validation failed!"
    echo '{"status":"ERROR","timestamp":"'$(date -Iseconds)'"}' > "$STATUS_FILE"
    exit 1
fi

log_section "Step 2: Starting VNC Services"

# Clean up old processes
log "Cleaning up old processes..."
pkill -9 Xvfb 2>/dev/null || true
pkill -9 x11vnc 2>/dev/null || true
pkill -9 websockify 2>/dev/null || true
pkill -9 fluxbox 2>/dev/null || true
pkill -9 qgis 2>/dev/null || true
rm -rf /tmp/.X* /tmp/runtime-root 2>/dev/null || true
sleep 2

# Start X server
log "Starting X server (Xvfb)..."
Xvfb :1 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset > /logs/xvfb.log 2>&1 &
sleep 3

# Start window manager
log "Starting window manager (Fluxbox)..."
DISPLAY=:1 fluxbox > /logs/fluxbox.log 2>&1 &
sleep 2

# Start VNC server
log "Starting VNC server (x11vnc)..."
x11vnc -display :1 -forever -nopw -listen localhost -rfbport 5900 -shared > /logs/x11vnc.log 2>&1 &
sleep 3

# Start web VNC
log "Starting web VNC (websockify)..."
websockify --web=/usr/share/novnc 8888 localhost:5900 > /logs/websockify.log 2>&1 &
sleep 3

# Start QGIS
log "Starting QGIS..."
DISPLAY=:1 LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none QT_QPA_PLATFORM=xcb qgis --nologo > /logs/qgis.log 2>&1 &
sleep 5

log_section "Step 3: Verifying Services"

# Verify all services
all_running=true

if pgrep -x "Xvfb" > /dev/null; then
    log "✓ Xvfb is running"
else
    log_error "✗ Xvfb is NOT running"
    all_running=false
fi

if pgrep -x "x11vnc" > /dev/null; then
    log "✓ x11vnc is running"
else
    log_error "✗ x11vnc is NOT running"
    all_running=false
fi

if pgrep -x "websockify" > /dev/null; then
    log "✓ websockify is running"
else
    log_error "✗ websockify is NOT running"
    all_running=false
fi

if pgrep -x "qgis" > /dev/null; then
    log "✓ QGIS is running"
else
    log_error "✗ QGIS is NOT running"
    all_running=false
fi

# Save status
if [ "$all_running" = true ]; then
    log_section "✓ ALL SYSTEMS READY!"
    log "Access QGIS at: http://localhost:8888/vnc.html"
    echo '{"status":"RUNNING","timestamp":"'$(date -Iseconds)'","url":"http://localhost:8888/vnc.html"}' > "$STATUS_FILE"
else
    log_error "Some services failed to start"
    echo '{"status":"PARTIAL","timestamp":"'$(date -Iseconds)'"}' > "$STATUS_FILE"
fi

# Keep container running
log "Container is running. Monitoring services..."
tail -f /dev/null