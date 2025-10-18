#!/bin/bash
# Network Connectivity Test Script

echo "🔍 ZEE5 Network Troubleshooting"
echo "================================"

# Get current IP
echo "📡 Current Network Configuration:"
ip addr show | grep -E "inet.*192\.168\." | head -3

echo -e "\n🐳 Docker Container Status:"
docker-compose ps

echo -e "\n🌐 Port Binding Check:"
sudo netstat -tlnp | grep :5052 || echo "❌ Port 5052 not bound"

echo -e "\n🏠 Local Access Test:"
curl -I http://localhost:5052/ 2>&1 | head -3

echo -e "\n🌍 Network Access Test:"
LOCAL_IP=$(ip route get 8.8.8.8 | sed -n '/src/{s/.*src *\([^ ]*\).*/\1/p;q}')
echo "Testing with IP: $LOCAL_IP"
curl -I http://$LOCAL_IP:5052/ 2>&1 | head -3

echo -e "\n🔒 Firewall Status:"
sudo ufw status 2>/dev/null || echo "UFW not active/installed"

echo -e "\n🔧 Environment Variables:"
cat .env 2>/dev/null || echo "No .env file found"

echo -e "\n💡 Recommended Actions:"
echo "1. If localhost works but network doesn't: Check firewall"
echo "2. If port not bound: Restart Docker Compose with 0.0.0.0 binding"
echo "3. If all fails: Use 'ip addr show' to find correct IP"