#!/usr/bin/env python3
"""
"""
import os
import sys
import time
from pathlib import Path

print("QGIS Docker Environment Starting...")

# Set environment for headless operation
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-root'

# Test QGIS Python API (not the GUI)
try:
    from qgis.core import Qgis, QgsApplication
    print(f"✓ QGIS {Qgis.version()} Python API ready")
    print("✓ Container is running in headless mode")
except ImportError as e:
    print(f"✗ Failed to load QGIS Python API: {e}")

# Keep container running
print("Container ready for commands. Use 'docker-compose exec qgis <command>'")
print("Examples:")
print("  docker-compose exec qgis qgis_process list")
print("  docker-compose exec qgis python3 /workspace/your_script.py")

# Keep the container alive
while True:
    time.sleep(3600)  # Sleep for an hour, repeat