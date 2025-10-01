#!/bin/bash
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
