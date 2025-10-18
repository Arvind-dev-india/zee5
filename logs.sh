#!/bin/bash

# ZEE5 Streaming Service - View Logs

echo "📋 ZEE5 Streaming Service Logs"
echo "==============================="
echo ""
echo "Press Ctrl+C to exit"
echo ""

# Detect Docker Compose command (v1 or v2)
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not installed."
    exit 1
fi

$DOCKER_COMPOSE_CMD logs -f zee5-app
