FROM qgis/qgis:3.34

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV QGIS_PREFIX_PATH=/usr
ENV QGIS_PLUGINPATH=/usr/share/qgis/python/plugins
ENV DISPLAY=:99

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    python3-pandas \
    python3-sklearn \
    python3-gdal \
    python3-pyqt5 \
    git \
    wget \
    curl \
    unzip \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Create working directories
RUN mkdir -p /workspace/data /workspace/projects /workspace/plugins /config /logs /scripts

# Install Python packages for EnMAP-Box
RUN pip3 install --break-system-packages \
    pyqtgraph \
    spectral \
    matplotlib \
    pyyaml \
    python-dotenv

# Install EnMAP-Box
RUN cd /usr/share/qgis/python/plugins && \
    git clone --depth 1 https://github.com/EnMAP-Box/enmap-box.git enmapbox || \
    echo "EnMAP-Box already exists or failed to clone"

# Set working directory
WORKDIR /workspace

# Keep container running
CMD ["tail", "-f", "/dev/null"]