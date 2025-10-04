# QGIS Docker Environment with EnMAP-Box

A fully containerized QGIS 3.34 LTR environment with EnMAP-Box plugin and required Python packages(later for preprocessing and postprocessing). Access QGIS through CLI or your web browser via noVNC or use a native VNC client for improved performance.
Available as a pre-built image on GitHub Container Registry or build from source.

## ✨ Features

- **QGIS 3.34 LTR** running in an isolated Docker container
- **EnMAP-Box plugin** pre-installed and configured
- **Dual access modes**: Web-based (noVNC) or native VNC client
- **CLI & GUI support** for flexible workflows
- **Cross-platform** compatibility (Windows, macOS, Linux)
- **Persistent storage** for profiles, projects, and workspace data
- **Pre-built Image** Available as a pre-built image on GitHub Container Registry just Pull and Run
-  **Startup Script** check status of upgrade, compatibility of software and work accordingly. For all required libraries

## 📋 Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- Docker Compose (included with Docker Desktop)
- *(Optional)* VNC client for better performance (e.g., [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/), [TigerVNC](https://tigervnc.org/))

## 🚀 Quick Start

### Option 1. Clone the Repository

```bash
git clone https://github.com/ihatecolddd/qgis-docker
cd qgis-docker
```



#### Build and Start the Container

```bash
docker-compose up -d
```

### Option 2. Use Pre-built Image
The pre-built image is hosted on GitHub Container Registry and requires no build process.

```bash
docker pull ghcr.io/ihatecolddd/qgis-docker:latest
```
### 1. Launch QGIS

**For macOS/Linux:**

```bash
chmod +x start-qgis.sh
./start-qgis.sh
```

**For Windows (PowerShell):**

```powershell
.\start-qgis.ps1
```

### 2. Access QGIS

**Option A: Web Browser (noVNC)**
- Open your browser and navigate to: `http://localhost:8888/vnc.html`
- Click **Connect** to access the QGIS desktop environment

**Option B: VNC Client (Better Performance)**
- Connect to: `localhost:5900`
- Password: *(check your docker-compose.yml for VNC password)*
- VNC clients provide smoother graphics and lower latency compared to the web browser



## Directory Structure

- `workspace` - Your GIS files
- `logs/` - Application logs
- `scripts/` - Utility scripts
- `docker/` - Docker configuration

## 🛠️ Usage Tips

- **Data persistence**: Place your data files in `workspace/data/` to access them from within QGIS
- **Save projects**: Store QGIS projects in `workspace/projects/` to persist between container restarts
- **Install plugins**: Additional plugins can be placed in `workspace/plugins/`
- **View logs**: Check `logs/` directory for troubleshooting

## 🔧 Common Commands

**Stop the container:**
```bash
docker-compose down
```

**Restart the container:**
```bash
docker-compose restart
```

**View container logs:**
```bash
docker-compose logs -f
```

**Rebuild the container (after Dockerfile changes):**
```bash
docker-compose up -d --build
```

## 🐛 Troubleshooting

- **Container won't start**: Ensure Docker Desktop is running and ports 5900 and 8888 are not in use
- **Can't connect via browser**: Check if the container is running with `docker-compose ps`
- **Performance issues in browser**: Use a native VNC client instead of the web interface
- **Data not persisting**: Verify that volume mounts are correct in `docker-compose.yml`

## 📝 Notes

- The web interface (noVNC) is convenient but may have slower performance compared to native VNC clients
- For production use or intensive work, a VNC application is recommended for better responsiveness
---

