FROM qgis/qgis:3.34

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV QGIS_PREFIX_PATH=/usr
ENV QGIS_PLUGINPATH=/usr/share/qgis/python/plugins
ENV DISPLAY=:1

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/data /workspace/projects /workspace/plugins \
    /config /logs /scripts /tests

RUN pip3 install --break-system-packages \
    dask \
    distributed \
    spectral \
    python-dotenv \
    pyqtgraph

RUN cd /usr/share/qgis/python/plugins && \
    git clone --depth 1 https://github.com/EnMAP-Box/enmap-box.git enmapbox || true

COPY scripts/startup_vnc.sh /scripts/startup_vnc.sh
RUN chmod +x /scripts/startup_vnc.sh

WORKDIR /workspace

CMD ["/scripts/startup_vnc.sh"]