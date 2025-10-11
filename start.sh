#!/bin/bash
# ZEE5 Docker Quick Start Script

echo "🚀 Starting ZEE5 Streaming Service..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Use docker-compose or docker compose
COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Get server host/port from environment or use defaults
SERVER_HOST=${SERVER_HOST:-localhost}
SERVER_PORT=${SERVER_PORT:-5052}

# Stop any existing containers
echo "🛑 Stopping existing containers..."
$COMPOSE_CMD down 2>/dev/null

# Build and start the containers
echo "🔨 Building and starting containers..."
$COMPOSE_CMD up -d --build

# Wait a moment for the service to start
echo "⏳ Waiting for service to start..."
sleep 3

# Check if the service is running
if curl -s -o /dev/null -w "%{http_code}" http://${SERVER_HOST}:${SERVER_PORT}/playlist.php | grep -q "200"; then
    echo ""
    echo "✅ ZEE5 Streaming Service is now running!"
    echo ""
    echo "🏠 Homepage: http://${SERVER_HOST}:${SERVER_PORT}/"
    echo "📺 M3U Playlist: http://${SERVER_HOST}:${SERVER_PORT}/playlist.php"
    echo "🎬 Individual Channel: http://${SERVER_HOST}:${SERVER_PORT}/stream.php?id=CHANNEL_ID"
    echo ""
    echo "🎯 For IPTV Players (VLC, Tivimate, etc.):"
    echo "   Use: http://${SERVER_HOST}:${SERVER_PORT}/playlist.php"
    echo ""
    echo "🌐 Network Configuration:"
    echo "   Current: SERVER_HOST=${SERVER_HOST}, SERVER_PORT=${SERVER_PORT}"
    echo "   To change: Edit .env file and restart"
    echo ""
    echo "🔧 For network access from 192.168.1.10 to 192.168.1.16:"
    echo "   Set SERVER_HOST=192.168.1.16 in .env file"
    echo ""
    echo "🛑 To stop the service, run: $COMPOSE_CMD down"
    echo ""
else
    echo "❌ Service failed to start. Check logs with: $COMPOSE_CMD logs"
    exit 1
fi