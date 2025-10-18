#!/bin/bash

# ZEE5 Streaming Service - Stop Script
echo "🛑 Stopping ZEE5 Streaming Service..."

# Change to docker directory
cd docker

# Stop containers
docker-compose down

echo "✅ Service stopped successfully!"
echo ""
echo "💡 To start again, run: ./scripts/start.sh"
