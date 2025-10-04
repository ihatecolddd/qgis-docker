#!/usr/bin/env python3
"""
Comprehensive startup script for QGIS Docker Environment
Checks upgrades, compatibility, and starts all services automatically
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
import importlib.metadata as metadata

# Color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class StartupManager:
    def __init__(self):
        self.log_file = Path("/logs/startup.log")
        self.status_file = Path("/config/system_status.json")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file
        with open(self.log_file, 'w') as f:
            f.write("=== QGIS Environment Startup ===\n")
    
    def log(self, message, color=Colors.GREEN):
        """Log message with timestamp and color"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_msg = f"{color}[{timestamp}]{Colors.NC} {message}"
        print(formatted_msg)
        
        # Write to log file without color codes
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def log_error(self, message):
        """Log error message"""
        self.log(f"ERROR: {message}", Colors.RED)
    
    def log_warning(self, message):
        """Log warning message"""
        self.log(f"WARNING: {message}", Colors.YELLOW)
    
    def log_section(self, title):
        """Log section header"""
        separator = "=" * 50
        self.log(f"\n{separator}", Colors.CYAN)
        self.log(title, Colors.CYAN)
        self.log(separator, Colors.CYAN)
    
    def check_package(self, package_name, import_name=None):
        """Check if a Python package is installed and return its version"""
        if import_name is None:
            import_name = package_name
        
        try:
            # Try to import the package
            __import__(import_name)
            version = metadata.version(package_name)
            self.log(f"✓ {package_name} installed (version: {version})")
            return True, version
        except ImportError:
            self.log_error(f"✗ {package_name} NOT installed (import failed)")
            return False, None
        except metadata.PackageNotFoundError:
            self.log_warning(f"✗ {package_name} installed but version unknown")
            return True, "unknown"
    
    def check_system_command(self, command):
        """Check if a system command exists"""
        try:
            result = subprocess.run(['which', command], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                self.log(f"✓ {command} available")
                return True
            else:
                self.log_error(f"✗ {command} NOT available")
                return False
        except Exception as e:
            self.log_error(f"✗ Error checking {command}: {e}")
            return False
    
    def check_python_packages(self):
        """Check all required Python packages"""
        self.log_section("Step 1: Checking Python Packages")
        
        required_packages = {
            'numpy': 'numpy',
            'scipy': 'scipy',
            'matplotlib': 'matplotlib',
            'pandas': 'pandas',
            'dask': 'dask',
            'distributed': 'distributed',
            'pyqtgraph': 'pyqtgraph',
            'spectral': 'spectral',
            'yaml': 'pyyaml',
            'dotenv': 'python-dotenv',
        }
        
        all_installed = True
        package_versions = {}
        
        for import_name, package_name in required_packages.items():
            installed, version = self.check_package(package_name, import_name)
            if installed:
                package_versions[package_name] = version
            else:
                all_installed = False
        
        return all_installed, package_versions
    
    def check_system_packages(self):
        """Check all required system packages"""
        self.log_section("Step 2: Checking System Packages")
        
        required_commands = ['Xvfb', 'x11vnc', 'websockify', 'fluxbox', 'qgis']
        all_installed = True
        
        for command in required_commands:
            if not self.check_system_command(command):
                all_installed = False
        
        return all_installed
    
    def verify_compatibility(self, package_versions):
        """Verify package compatibility"""
        self.log_section("Step 3: Verifying Package Compatibility")
        
        # Define minimum required versions
        min_versions = {
            'numpy': '1.19.0',
            'scipy': '1.5.0',
            'matplotlib': '3.0.0',
            'pandas': '1.0.0',
            'dask': '2021.0.0',
            'pyqtgraph': '0.11.0',
        }
        
        compatible = True
        for package, min_version in min_versions.items():
            if package in package_versions:
                current = package_versions[package]
                if current != "unknown":
                    # Simple version comparison (works for most cases)
                    try:
                        from packaging import version
                        if version.parse(current) >= version.parse(min_version):
                            self.log(f"✓ {package} {current} >= {min_version}")
                        else:
                            self.log_error(f"✗ {package} {current} < {min_version}")
                            compatible = False
                    except:
                        # If packaging not available, just log the version
                        self.log(f"~ {package} {current} (min: {min_version})")
            else:
                self.log_error(f"✗ {package} not found")
                compatible = False
        
        if compatible:
            self.log("✓ All packages meet minimum version requirements")
        else:
            self.log_warning("Some packages may need upgrading")
        
        return compatible
    
    def check_qgis_plugins(self):
        """Check QGIS plugins"""
        self.log_section("Step 4: Checking QGIS Plugins")
        
        plugin_path = Path("/usr/share/qgis/python/plugins/enmapbox")
        
        if plugin_path.exists():
            self.log("✓ EnMAP-Box plugin found")
            return True
        else:
            self.log_warning("EnMAP-Box plugin not found, will be installed later")
            return False
    
    def upgrade_packages(self):
        """Upgrade packages if needed"""
        self.log_section("Upgrading Packages")
        
        requirements_file = Path("/tmp/requirements.txt")
        if requirements_file.exists():
            try:
                self.log("Running pip upgrade...")
                result = subprocess.run(
                    ['pip3', 'install', '--break-system-packages', '--upgrade', 
                     '-r', str(requirements_file)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    self.log("✓ Package upgrade completed successfully")
                    return True
                else:
                    self.log_error(f"Package upgrade failed: {result.stderr}")
                    return False
            except Exception as e:
                self.log_error(f"Error upgrading packages: {e}")
                return False
        else:
            self.log_warning("No requirements.txt found, skipping upgrade")
            return True
    
    def cleanup_processes(self):
        """Clean up any existing processes"""
        self.log("Cleaning up old processes...")
        
        processes = ['Xvfb', 'x11vnc', 'websockify', 'fluxbox', 'qgis']
        for proc in processes:
            try:
                subprocess.run(['pkill', '-9', proc], 
                             capture_output=True, 
                             timeout=5)
            except:
                pass
        
        # Clean up X11 temp files
        try:
            subprocess.run(['rm', '-rf', '/tmp/.X*', '/tmp/runtime-root'], 
                         capture_output=True, 
                         timeout=5)
        except:
            pass
        
        time.sleep(2)
        self.log("✓ Cleanup completed")
    
    def start_service(self, name, command, log_file, wait_time=3):
        """Start a service and log output"""
        self.log(f"Starting {name}...")
        
        try:
            log_path = Path(f"/logs/{log_file}")
            with open(log_path, 'w') as f:
                subprocess.Popen(
                    command,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    shell=True,
                    env=os.environ.copy()
                )
            
            time.sleep(wait_time)
            self.log(f"✓ {name} started")
            return True
        except Exception as e:
            self.log_error(f"Failed to start {name}: {e}")
            return False
    
    def verify_service(self, process_name):
        """Verify if a service is running"""
        try:
            result = subprocess.run(
                ['pgrep', '-x', process_name],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def start_services(self):
        """Start all required services"""
        self.log_section("Step 5: Starting Services")
        
        # Clean up first
        self.cleanup_processes()
        
        # Start X server
        if not self.start_service(
            "X server (Xvfb)",
            "Xvfb :1 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset",
            "xvfb.log",
            3
        ):
            return False
        
        # Start window manager
        if not self.start_service(
            "Window manager (Fluxbox)",
            "DISPLAY=:1 fluxbox",
            "fluxbox.log",
            2
        ):
            return False
        
        # Start VNC server
        if not self.start_service(
            "VNC server (x11vnc)",
            "x11vnc -display :1 -forever -nopw -listen localhost -rfbport 5900 -shared",
            "x11vnc.log",
            3
        ):
            return False
        
        # Start web VNC
        if not self.start_service(
            "Web VNC (websockify)",
            "websockify --web=/usr/share/novnc 8888 localhost:5900",
            "websockify.log",
            3
        ):
            return False
        
        # Start QGIS
        if not self.start_service(
            "QGIS",
            "DISPLAY=:1 LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none QT_QPA_PLATFORM=xcb qgis --nologo",
            "qgis.log",
            5
        ):
            return False
        
        return True
    
    def verify_all_services(self):
        """Verify all services are running"""
        self.log_section("Step 6: Verifying Services")
        
        services = {
            'Xvfb': 'Xvfb',
            'x11vnc': 'x11vnc',
            'websockify': 'websockify',
            'QGIS': 'qgis'
        }
        
        all_running = True
        for name, process in services.items():
            if self.verify_service(process):
                self.log(f"✓ {name} is running")
            else:
                self.log_error(f"✗ {name} is NOT running")
                all_running = False
        
        return all_running
    
    def save_status(self, status, package_versions=None):
        """Save system status to JSON file"""
        try:
            # Get QGIS version
            qgis_version = "unknown"
            try:
                result = subprocess.run(['qgis', '--version'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    qgis_version = result.stdout.strip()
            except:
                pass
            
            # Get Python version
            python_version = sys.version.split()[0]
            
            status_data = {
                "last_check": datetime.now().isoformat(),
                "status": status,
                "qgis_version": qgis_version,
                "python_version": python_version,
                "packages": package_versions or {}
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
            
            self.log(f"Status saved to {self.status_file}")
        except Exception as e:
            self.log_error(f"Failed to save status: {e}")
    
    def run(self):
        """Main startup sequence"""
        try:
            self.log("=" * 50, Colors.CYAN)
            self.log("QGIS Docker Environment Starting...", Colors.CYAN)
            self.log("=" * 50, Colors.CYAN)
            
            # Step 1: Check Python packages
            packages_ok, package_versions = self.check_python_packages()
            
            if not packages_ok:
                self.log_warning("Some packages missing, attempting to install...")
                self.upgrade_packages()
                packages_ok, package_versions = self.check_python_packages()
            
            # Step 2: Check system packages
            system_ok = self.check_system_packages()
            
            if not system_ok:
                self.log_error("System packages missing. Please rebuild container.")
                self.save_status("FAILED", package_versions)
                return False
            
            # Step 3: Verify compatibility
            compatibility_ok = self.verify_compatibility(package_versions)
            
            if not compatibility_ok:
                self.log_warning("Some compatibility issues found")
            
            # Step 4: Check plugins
            self.check_qgis_plugins()
            
            # Step 5 & 6: Start and verify services
            if self.start_services():
                if self.verify_all_services():
                    self.log_section("✓ ALL SYSTEMS READY!")
                    self.log("Access QGIS at: http://localhost:8888/vnc.html", Colors.GREEN)
                    self.save_status("RUNNING", package_versions)
                    
                    # Keep container running
                    self.log("\nContainer is running. Monitoring services...", Colors.CYAN)
                    while True:
                        time.sleep(60)
                else:
                    self.log_error("Some services failed to start")
                    self.log_error("Check logs in /logs/ directory")
                    self.save_status("PARTIAL", package_versions)
                    return False
            else:
                self.log_error("Failed to start services")
                self.save_status("FAILED", package_versions)
                return False
            
        except KeyboardInterrupt:
            self.log("\nShutdown requested", Colors.YELLOW)
            self.save_status("STOPPED", package_versions)
            return True
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            self.save_status("ERROR")
            return False

if __name__ == "__main__":
    manager = StartupManager()
    success = manager.run()
    sys.exit(0 if success else 1)