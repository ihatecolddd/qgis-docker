#!/bin/bash

IMAGE="ghcr.io/ihatecolddd/qgis-docker:latest"
CONTAINER="qgis-enmap-container"

echo "=========================================="
echo "  QGIS Docker Environment"
echo "=========================================="

echo "Pulling latest image..."
docker pull $IMAGE

echo "Starting QGIS..."
docker-compose up -d

echo "Waiting for startup (25 seconds)..."
sleep 25

echo ""
echo "=========================================="
docker logs $CONTAINER --tail 50

echo ""
echo "Opening browser: http://localhost:8888/vnc.html"
open "http://localhost:8888/vnc.html"

echo ""
echo "Commands:"
echo "  docker logs $CONTAINER -f"
echo "  docker-compose down"