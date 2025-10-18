#!/bin/bash

# ZEE5 Streaming Service - Stop Script

echo "🛑 Stopping ZEE5 Streaming Service..."
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

$DOCKER_COMPOSE_CMD down

echo ""
echo "✅ Service stopped successfully!"
echo ""
echo "💡 Commands:"
echo "   Start again:        ./start.sh"
echo "   Remove all data:    $DOCKER_COMPOSE_CMD down -v"
echo "   Remove images too:  $DOCKER_COMPOSE_CMD down -v --rmi all"
echo ""
