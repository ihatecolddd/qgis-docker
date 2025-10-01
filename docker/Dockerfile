FROM --platform=$BUILDPLATFORM qgis/qgis:3.34 AS base

ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG TARGETARCH

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV QGIS_PREFIX_PATH=/usr
ENV QGIS_PLUGINPATH=/usr/share/qgis/python/plugins
ENV DISPLAY=:99

RUN apt-get update && apt-get install -y \
    python3-pip python3-dev python3-numpy python3-scipy \
    python3-matplotlib python3-pandas python3-sklearn \
    python3-gdal python3-rasterio python3-fiona \
    python3-shapely python3-pyproj \
    git wget curl unzip vim xvfb x11vnc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/data /workspace/projects /workspace/plugins /config /logs /scripts

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY scripts/install_enmap.sh /scripts/
RUN chmod +x /scripts/install_enmap.sh && /scripts/install_enmap.sh

COPY scripts/*.py /scripts/
RUN chmod +x /scripts/*.py

WORKDIR /workspace

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 /scripts/validate_environment.py --quick || exit 1

ENTRYPOINT ["python3", "/scripts/startup.py"]
CMD ["qgis"]
