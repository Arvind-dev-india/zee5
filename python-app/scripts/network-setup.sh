#!/bin/bash

# Network Setup Helper Script
echo "🌐 ZEE5 Streaming Service - Network Setup"
echo "=========================================="
echo ""

# Get server IP addresses
echo "📡 Detecting network interfaces..."
echo ""

# Linux/Mac
if command -v ip &> /dev/null; then
    echo "Available IP addresses:"
    ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | while read -r ip; do
        echo "  • $ip"
    done
elif command -v ifconfig &> /dev/null; then
    echo "Available IP addresses:"
    ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | while read -r ip; do
        echo "  • $ip"
    done
fi

echo ""
echo "🔧 Configuration Steps:"
echo ""
echo "1. Choose your server IP from above"
echo ""
echo "2. Update .env file:"
echo "   SERVER_URL=http://YOUR_IP:5052"
echo ""
echo "3. Example for IP 192.168.1.100:"
echo "   SERVER_URL=http://192.168.1.100:5052"
echo ""
echo "4. Restart service:"
echo "   ./scripts/stop.sh && ./scripts/start.sh"
echo ""
echo "📺 Access from other devices:"
echo "   Playlist: http://YOUR_IP:5052/playlist.m3u"
echo "   Homepage: http://YOUR_IP:5052/"
echo ""
echo "🔒 Firewall Configuration:"
echo "   Make sure port 5052 is open:"
echo ""
echo "   Ubuntu/Debian:"
echo "     sudo ufw allow 5052/tcp"
echo ""
echo "   CentOS/RHEL:"
echo "     sudo firewall-cmd --permanent --add-port=5052/tcp"
echo "     sudo firewall-cmd --reload"
echo ""
echo "   Docker:"
echo "     Port is already configured in docker-compose.yml"
echo ""
