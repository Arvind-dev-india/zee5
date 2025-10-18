#!/bin/bash

# ZEE5 Streaming Service - Start Script
echo "🚀 Starting ZEE5 Streaming Service..."

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
fi

# Change to docker directory
cd docker

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🔍 Checking service health..."
docker-compose ps

# Show logs
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose logs --tail=20

echo ""
echo "✅ ZEE5 Streaming Service started!"
echo ""
echo "🌐 Access the service at:"
echo "   Homepage:  http://localhost:5052/"
echo "   Playlist:  http://localhost:5052/playlist.m3u"
echo "   Health:    http://localhost:5052/health"
echo "   Debug:     http://localhost:5052/debug"
echo ""
echo "📝 View logs: docker-compose -f docker/docker-compose.yml logs -f"
echo "🛑 Stop service: ./stop.sh"
