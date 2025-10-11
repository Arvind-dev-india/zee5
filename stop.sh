#!/bin/bash
# ZEE5 Docker Stop Script

echo "🛑 Stopping ZEE5 Streaming Service..."

# Use docker-compose or docker compose
COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

# Stop and remove containers
$COMPOSE_CMD down

echo "✅ ZEE5 Streaming Service stopped."
echo ""
echo "🚀 To start again, run: ./start.sh"