# QGIS Docker Environment

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
