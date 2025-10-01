#!/usr/bin/env python3
"""
Automated Setup Script for QGIS Docker Environment
Windows-compatible version (no Unicode characters)
Works on both Mac and Windows
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

# Set UTF-8 encoding for Windows
if platform.system() == "Windows":
    sys.stdout.reconfigure(encoding='utf-8')

# Detect operating system
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"

def create_directory_structure():
    """Create all necessary directories"""
    print("Creating directory structure...")
    
    directories = [
        "docker",
        "scripts", 
        "config",
        "workspace/data",
        "workspace/projects",
        "workspace/plugins",
        "logs",
        "tests",
        ".github/workflows"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  [OK] Created {dir_path}")
    
    # Create .gitkeep files
    gitkeep_dirs = [
        "workspace/data",
        "workspace/projects", 
        "workspace/plugins",
        "logs"
    ]
    
    for dir_path in gitkeep_dirs:
        (Path(dir_path) / ".gitkeep").touch()

def create_dockerfile():
    """Create Dockerfile"""
    print("\nCreating Dockerfile...")
    
    dockerfile_content = '''FROM --platform=$BUILDPLATFORM qgis/qgis:3.34 AS base

ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG TARGETARCH

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV QGIS_PREFIX_PATH=/usr
ENV QGIS_PLUGINPATH=/usr/share/qgis/python/plugins
ENV DISPLAY=:99

RUN apt-get update && apt-get install -y \\
    python3-pip python3-dev python3-numpy python3-scipy \\
    python3-matplotlib python3-pandas python3-sklearn \\
    python3-gdal python3-rasterio python3-fiona \\
    python3-shapely python3-pyproj \\
    git wget curl unzip vim xvfb x11vnc \\
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/data /workspace/projects /workspace/plugins /config /logs /scripts

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && \\
    pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY scripts/install_enmap.sh /scripts/
RUN chmod +x /scripts/install_enmap.sh && /scripts/install_enmap.sh

COPY scripts/*.py /scripts/
RUN chmod +x /scripts/*.py

WORKDIR /workspace

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python3 /scripts/validate_environment.py --quick || exit 1

ENTRYPOINT ["python3", "/scripts/startup.py"]
CMD ["qgis"]
'''
    
    with open("docker/Dockerfile", "w", encoding='utf-8') as f:
        f.write(dockerfile_content)
    print("  [OK] Dockerfile created")

def create_docker_compose():
    """Create docker-compose.yml"""
    print("\nCreating docker-compose.yml...")
    
    # Detect platform
    if IS_MAC and platform.machine() == "arm64":
        default_platform = "linux/arm64"
    else:
        default_platform = "linux/amd64"
    
    compose_content = f'''version: '3.8'

services:
  qgis:
    build:
      context: .
      dockerfile: docker/Dockerfile
      platforms:
        - linux/amd64
        - linux/arm64
    image: qgis-enmap:3.34-ltr
    container_name: qgis-enmap-container
    platform: {default_platform}
    
    environment:
      - DISPLAY=${{DISPLAY:-:99}}
      - QT_QPA_PLATFORM=${{QT_QPA_PLATFORM:-offscreen}}
      - PYTHONPATH=/workspace/plugins:/usr/share/qgis/python/plugins
      - QGIS_LOG_FILE=/logs/qgis.log
      - VALIDATION_LOG=/logs/validation.log
      - TZ=${{TZ:-UTC}}
    
    volumes:
      - ./workspace:/workspace
      - ./logs:/logs
      - ./config:/config
      - qgis-profiles:/root/.local/share/QGIS/QGIS3
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
    
    ports:
      - "5900:5900"
      - "8888:8888"
    
    networks:
      - qgis-network
    
    restart: unless-stopped
    
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G

volumes:
  qgis-profiles:
    driver: local

networks:
  qgis-network:
    driver: bridge
'''
    
    with open("docker-compose.yml", "w", encoding='utf-8') as f:
        f.write(compose_content)
    print(f"  [OK] docker-compose.yml created (platform: {default_platform})")

def create_requirements():
    """Create requirements.txt"""
    print("\nCreating requirements.txt...")
    
    requirements = '''numpy==1.24.3
scipy==1.10.1
pandas==2.0.3
scikit-learn==1.3.0
matplotlib==3.7.2
seaborn==0.12.2
rasterio==1.3.8
fiona==1.9.4
shapely==2.0.1
geopandas==0.13.2
pyproj==3.6.0
scikit-image==0.21.0
opencv-python-headless==4.8.0.74
pillow==10.0.0
spectral==0.23.1
h5py==3.9.0
netCDF4==1.6.4
pyyaml==6.0.1
python-dotenv==1.0.0
'''
    
    with open("docker/requirements.txt", "w", encoding='utf-8') as f:
        f.write(requirements)
    print("  [OK] requirements.txt created")

def create_scripts():
    """Create all script files"""
    print("\nCreating scripts...")
    
    # install_enmap.sh
    install_enmap = '''#!/bin/bash
set -e

ENMAP_VERSION="3.13.0"
ENMAP_URL="https://github.com/EnMAP-Box/enmap-box/archive/refs/tags/v${ENMAP_VERSION}.tar.gz"

echo "Installing EnMAP-Box version ${ENMAP_VERSION}..."

mkdir -p /usr/share/qgis/python/plugins
cd /tmp
wget -q ${ENMAP_URL} -O enmap-box.tar.gz || curl -sL ${ENMAP_URL} -o enmap-box.tar.gz
tar -xzf enmap-box.tar.gz
mv enmap-box-${ENMAP_VERSION}/enmapbox /usr/share/qgis/python/plugins/
rm -rf /tmp/enmap-box*

echo "EnMAP-Box installation completed!"
'''
    
    with open("scripts/install_enmap.sh", "w", newline='\n', encoding='utf-8') as f:
        f.write(install_enmap)
    
    # startup.py
    startup_py = '''#!/usr/bin/env python3
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
    f.write(f"{datetime.datetime.now()} - Environment started\\n")

# Start services
if len(sys.argv) > 1:
    cmd = sys.argv[1:]
    subprocess.run(cmd)
else:
    print("Environment ready!")
'''
    
    with open("scripts/startup.py", "w", encoding='utf-8') as f:
        f.write(startup_py)
    
    # validate_environment.py
    validate_py = '''#!/usr/bin/env python3
import sys
import argparse

def quick_check():
    try:
        import qgis.core
        import numpy
        import pandas
        print("[OK] Quick validation passed")
        return True
    except ImportError as e:
        print(f"[ERROR] Quick validation failed: {e}")
        return False

def full_check():
    print("Running full validation...")
    quick_check()
    
    # Check directories
    import os
    from pathlib import Path
    
    dirs = ["/workspace", "/logs", "/config"]
    for d in dirs:
        if Path(d).exists():
            print(f"[OK] Directory exists: {d}")
        else:
            print(f"[ERROR] Directory missing: {d}")
    
    # Check Python packages
    packages = ["numpy", "scipy", "pandas", "rasterio", "geopandas"]
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"[OK] Package {pkg} installed")
        except ImportError:
            print(f"[ERROR] Package {pkg} not found")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    
    if args.quick:
        sys.exit(0 if quick_check() else 1)
    else:
        sys.exit(0 if full_check() else 1)
'''
    
    with open("scripts/validate_environment.py", "w", encoding='utf-8') as f:
        f.write(validate_py)
    
    # Create test_environment.py
    test_py = '''#!/usr/bin/env python3
import unittest
import sys
import platform

class TestEnvironment(unittest.TestCase):
    def test_qgis_import(self):
        """Test QGIS can be imported"""
        try:
            from qgis.core import QgsApplication, Qgis
            self.assertIsNotNone(QgsApplication)
        except ImportError as e:
            self.fail(f"Failed to import QGIS: {e}")
    
    def test_python_packages(self):
        """Test required Python packages"""
        packages = ["numpy", "scipy", "pandas", "rasterio"]
        for package in packages:
            with self.subTest(package=package):
                try:
                    __import__(package)
                except ImportError:
                    self.fail(f"Package {package} not installed")

if __name__ == "__main__":
    unittest.main(verbosity=2)
'''
    
    with open("tests/test_environment.py", "w", encoding='utf-8') as f:
        f.write(test_py)
    
    print("  [OK] Created install_enmap.sh")
    print("  [OK] Created startup.py")
    print("  [OK] Created validate_environment.py")
    print("  [OK] Created test_environment.py")

def create_env_file():
    """Create .env file"""
    print("\nCreating .env file...")
    
    # Detect platform
    if IS_MAC and platform.machine() == "arm64":
        platform_setting = "linux/arm64"
    else:
        platform_setting = "linux/amd64"
    
    env_content = f'''DOCKER_DEFAULT_PLATFORM={platform_setting}
BUILDPLATFORM={platform_setting}
TARGETPLATFORM={platform_setting}
DISPLAY=:99
QT_QPA_PLATFORM=offscreen
DOCKER_MEMORY=8g
DOCKER_CPUS=4
TZ=UTC
DEBUG=0
'''
    
    with open(".env", "w", encoding='utf-8') as f:
        f.write(env_content)
    print(f"  [OK] .env created (platform: {platform_setting})")

def create_gitignore():
    """Create .gitignore"""
    print("\nCreating .gitignore...")
    
    gitignore = '''# Python
__pycache__/
*.py[cod]
.Python
env/
venv/

# QGIS
*.qgs~
*.qgz~

# Data
workspace/data/*
!workspace/data/.gitkeep
*.tif
*.shp
*.gpkg

# Logs
logs/*
!logs/.gitkeep

# Environment
.env.local
.DS_Store
'''
    
    with open(".gitignore", "w", encoding='utf-8') as f:
        f.write(gitignore)
    print("  [OK] .gitignore created")

def create_readme():
    """Create README.md"""
    print("\nCreating README.md...")
    
    readme = '''# QGIS Docker Environment

QGIS 3.34 LTR with EnMAP-Box in Docker.

## Quick Start

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Validate
docker-compose exec qgis python3 /scripts/validate_environment.py

# Stop
docker-compose down
```

## Directory Structure

- `workspace/` - Your GIS files
- `logs/` - Application logs
- `scripts/` - Utility scripts
- `docker/` - Docker configuration

## Usage

Place your data in `workspace/data/` and run:

```bash
docker-compose exec qgis python3 /workspace/your_script.py
```
'''
    
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(readme)
    print("  [OK] README.md created")

def check_docker():
    """Check if Docker is installed"""
    print("\nChecking Docker installation...")
    
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, 
                              shell=IS_WINDOWS)
        if result.returncode == 0:
            print(f"  [OK] Docker found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"  [WARNING] Could not check Docker: {e}")
        return False
    
    print("  [WARNING] Docker not found!")
    print("\nPlease install Docker Desktop:")
    print("  Mac: https://docs.docker.com/desktop/install/mac-install/")
    print("  Windows: https://docs.docker.com/desktop/install/windows-install/")
    return False

def build_docker_image():
    """Build the Docker image"""
    print("\nBuilding Docker image...")
    print("  This may take 10-15 minutes on first run...")
    
    try:
        result = subprocess.run(
            ["docker-compose", "build"],
            shell=IS_WINDOWS
        )
        if result.returncode == 0:
            print("  [OK] Docker image built successfully!")
            return True
        else:
            print("  [ERROR] Build failed. Check the errors above.")
            return False
    except Exception as e:
        print(f"  [ERROR] Build failed: {e}")
        return False

def main():
    """Main setup function"""
    print("="*60)
    print("QGIS DOCKER ENVIRONMENT - AUTOMATED SETUP")
    print("="*60)
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"\nWorking directory: {current_dir}")
    
    # Check if we're in an empty or new directory
    existing_files = list(current_dir.glob("*"))
    script_name = Path(__file__).name
    existing_files = [f for f in existing_files if f.name != script_name]
    
    if len(existing_files) > 0:
        print("\n[WARNING] Directory is not empty!")
        print("Existing files:", [f.name for f in existing_files[:5]])
        response = input("Continue anyway? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    try:
        # Create everything
        create_directory_structure()
        create_dockerfile()
        create_docker_compose()
        create_requirements()
        create_scripts()
        create_env_file()
        create_gitignore()
        create_readme()
        
        # Check Docker
        docker_available = check_docker()
        
        # Initialize git
        print("\nInitializing Git repository...")
        try:
            subprocess.run(["git", "init"], shell=IS_WINDOWS, capture_output=True)
            subprocess.run(["git", "add", "."], shell=IS_WINDOWS, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], shell=IS_WINDOWS, capture_output=True)
            print("  [OK] Git repository initialized")
        except:
            print("  [INFO] Git not installed or initialization skipped")
        
        # Summary
        print("\n" + "="*60)
        print("SETUP COMPLETE!")
        print("="*60)
        print("\nAll files have been created successfully!")
        print("\nNext steps:")
        print("  1. Build the Docker image: docker-compose build")
        print("  2. Start the container: docker-compose up -d")
        print("  3. Validate: docker-compose exec qgis python3 /scripts/validate_environment.py")
        
        if docker_available:
            response = input("\nBuild Docker image now? (y/n): ").lower()
            if response == 'y':
                build_docker_image()
                print("\nSetup and build complete!")
                print("Run 'docker-compose up -d' to start the environment.")
            else:
                print("\nSetup complete!")
                print("Run 'docker-compose build' when you're ready to build.")
        else:
            print("\nSetup complete!")
            print("Install Docker Desktop, then run 'docker-compose build'")
            
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Error during setup: {e}")
        sys.exit(1)