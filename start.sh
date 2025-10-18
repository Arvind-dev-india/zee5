#!/bin/bash

# ZEE5 Streaming Service - Start Script (Python FastAPI Version)
# This script starts the complete ZEE5 streaming service with Docker Compose

echo "🚀 Starting ZEE5 Streaming Service (Python FastAPI)..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed (v1 or v2)
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Update SERVER_URL in .env file with your server IP"
    echo "   Example: SERVER_URL=http://192.168.1.16:5052"
    echo ""
fi

# Get server IP for reference
echo "📡 Your server IP addresses:"
if command -v ip &> /dev/null; then
    ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | while read -r ip; do
        echo "   • $ip"
    done
elif command -v ifconfig &> /dev/null; then
    ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | sed 's/addr://' | while read -r ip; do
        echo "   • $ip"
    done
fi
echo ""

# Build and start services
echo "🐳 Building and starting Docker containers..."
echo "   This may take 2-3 minutes on first run (downloading images, building, installing Playwright)..."
echo ""

$DOCKER_COMPOSE_CMD up -d --build

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to start containers. Check the error above."
    exit 1
fi

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to initialize (60 seconds)..."
sleep 10

# Check status
echo ""
echo "📊 Container Status:"
$DOCKER_COMPOSE_CMD ps

# Wait a bit more for full initialization
sleep 5

# Check health
echo ""
echo "🔍 Checking service health..."
for i in {1..12}; do
    if curl -s http://localhost:5052/health > /dev/null 2>&1; then
        echo "✅ Service is healthy and ready!"
        break
    else
        if [ $i -eq 12 ]; then
            echo "⚠️  Service may still be starting. This is normal on first run."
            echo "   Cookie generation can take 30-60 seconds."
        else
            echo "   Waiting for service to be ready... ($i/12)"
            sleep 5
        fi
    fi
done

echo ""
echo "✅ ZEE5 Streaming Service is running!"
echo ""
echo "🌐 Access URLs:"
echo "   Homepage:     http://localhost:5052/"
echo "   M3U Playlist: http://localhost:5052/playlist.m3u"
echo "   Debug Page:   http://localhost:5052/debug"
echo "   Health Check: http://localhost:5052/health"
echo "   API Docs:     http://localhost:5052/docs"
echo ""
echo "📱 For network access from other devices:"
echo "   1. Note your server IP from above (e.g., 192.168.1.16)"
echo "   2. Edit .env file: SERVER_URL=http://192.168.1.16:5052"
echo "   3. Restart: ./stop.sh && ./start.sh"
echo "   4. Use: http://192.168.1.16:5052/playlist.m3u in your IPTV player"
echo ""
echo "📝 Useful commands:"
echo "   View logs:    $DOCKER_COMPOSE_CMD logs -f zee5-app"
echo "               or ./logs.sh"
echo "   Stop service: ./stop.sh"
echo "   Restart:      ./stop.sh && ./start.sh"
echo ""
echo "📖 Documentation:"
echo "   • DOCKER-SETUP.md - Complete Docker guide"
echo "   • python-app/README.md - Full documentation"
echo "   • python-app/NETWORK-ACCESS.md - Network setup guide"
echo ""