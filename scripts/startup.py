#!/usr/bin/env python3
import os
import sys
import json
import datetime
import subprocess
from pathlib import Path

print("Starting QGIS Docker environment...")
print(f"Timestamp: {datetime.datetime.now()}")
print(f"Platform: {os.environ.get('TARGETPLATFORM', 'unknown')}")

# Basic validation
try:
    from qgis.core import Qgis
    print(f"[OK] QGIS {Qgis.version()} loaded")
except ImportError as e:
    print(f"[ERROR] Failed to load QGIS: {e}")
    sys.exit(1)

# Create log directory if it doesn't exist
Path("/logs").mkdir(exist_ok=True)

# Log startup
log_file = Path("/logs/startup.log")
with open(log_file, "a") as f:
    f.write(f"{datetime.datetime.now()} - Environment started\n")

# Start services
if len(sys.argv) > 1:
    cmd = sys.argv[1:]
    subprocess.run(cmd)
else:
    print("Environment ready!")
