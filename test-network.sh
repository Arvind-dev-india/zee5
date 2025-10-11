#!/bin/bash
# Simple Network Test Script for ZEE5

echo "🔍 ZEE5 Network Test"
echo "==================="

# Get actual IP
ACTUAL_IP=$(hostname -I | awk '{print $1}')
echo "🌐 Detected Server IP: $ACTUAL_IP"

# Check .env configuration
echo -e "\n📝 Current .env configuration:"
cat .env 2>/dev/null || echo "❌ No .env file found"

# Check Docker status
echo -e "\n🐳 Docker Container Status:"
docker-compose ps 2>/dev/null || echo "❌ Docker Compose not running"

# Test local access
echo -e "\n🏠 Testing Local Access (localhost:5052):"
if timeout 5 curl -s -o /dev/null -w "%{http_code}" http://localhost:5052/ 2>/dev/null; then
    echo "✅ localhost:5052 - HTTP $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5052/)"
else
    echo "❌ localhost:5052 - Failed to connect"
fi

# Test network access with actual IP
echo -e "\n🌍 Testing Network Access ($ACTUAL_IP:5052):"
if timeout 5 curl -s -o /dev/null -w "%{http_code}" http://$ACTUAL_IP:5052/ 2>/dev/null; then
    echo "✅ $ACTUAL_IP:5052 - HTTP $(curl -s -o /dev/null -w "%{http_code}" http://$ACTUAL_IP:5052/)"
else
    echo "❌ $ACTUAL_IP:5052 - Failed to connect"
fi

# Check port binding
echo -e "\n🔌 Port Binding Check:"
if ss -tlnp 2>/dev/null | grep -q :5052; then
    echo "✅ Port 5052 is bound"
    ss -tlnp | grep :5052
else
    echo "❌ Port 5052 not found"
fi

# Test Docker logs
echo -e "\n📋 Recent Docker Logs:"
docker-compose logs --tail=5 zee5-app 2>/dev/null || echo "❌ Cannot access Docker logs"

# Recommendations
echo -e "\n💡 Quick Fixes:"
echo "1. Update .env with correct IP: echo 'SERVER_HOST=$ACTUAL_IP' > .env"
echo "2. Restart service: docker-compose down && docker-compose up -d"
echo "3. Test access: curl http://$ACTUAL_IP:5052/"
echo "4. For VLC: http://$ACTUAL_IP:5052/playlist.php"