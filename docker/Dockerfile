FROM qgis/qgis:3.34

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV QGIS_PREFIX_PATH=/usr
ENV QGIS_PLUGINPATH=/usr/share/qgis/python/plugins
ENV DISPLAY=:99

# Install system dependencies and EnMAP-Box dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    unzip \
    vim \
    xvfb \
    x11vnc \
    && rm -rf /var/lib/apt/lists/*

# Create working directories
RUN mkdir -p /workspace/data /workspace/projects /workspace/plugins /config /logs /scripts

# Skip requirements.txt for now - most packages are already in QGIS image
# If you need specific packages, add them one by one

# Create a simple install script for EnMAP-Box
RUN echo '#!/bin/bash\n\
echo "Installing EnMAP-Box..."\n\
cd /tmp\n\
wget -q https://github.com/EnMAP-Box/enmap-box/archive/refs/tags/v3.13.0.tar.gz -O enmap.tar.gz || echo "Download failed"\n\
if [ -f enmap.tar.gz ]; then\n\
    tar -xzf enmap.tar.gz\n\
    mkdir -p /usr/share/qgis/python/plugins\n\
    mv enmap-box-3.13.0/enmapbox /usr/share/qgis/python/plugins/ 2>/dev/null || true\n\
fi\n\
echo "EnMAP-Box installation attempted"' > /scripts/install_enmap.sh && \
    chmod +x /scripts/install_enmap.sh && \
    /scripts/install_enmap.sh

# Create a simple startup script
RUN echo '#!/usr/bin/env python3\n\
import sys\n\
print("QGIS Docker Environment Started")\n\
try:\n\
    from qgis.core import Qgis\n\
    print(f"QGIS {Qgis.version()} ready")\n\
except:\n\
    print("QGIS not available")\n\
if len(sys.argv) > 1:\n\
    import subprocess\n\
    subprocess.run(sys.argv[1:])' > /scripts/startup.py && \
    chmod +x /scripts/startup.py

# Create validation script
RUN echo '#!/usr/bin/env python3\n\
import sys\n\
try:\n\
    from qgis.core import Qgis\n\
    print(f"[OK] QGIS {Qgis.version()}")\n\
    import numpy\n\
    print("[OK] NumPy available")\n\
    import gdal\n\
    print("[OK] GDAL available")\n\
    sys.exit(0)\n\
except Exception as e:\n\
    print(f"[ERROR] {e}")\n\
    sys.exit(1)' > /scripts/validate_environment.py && \
    chmod +x /scripts/validate_environment.py

WORKDIR /workspace

ENTRYPOINT ["python3", "/scripts/startup.py"]
CMD ["qgis"]