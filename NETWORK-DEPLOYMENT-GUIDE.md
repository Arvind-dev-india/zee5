# 🌐 Network Deployment Guide

## 🎯 **Scenario: VM Server → Network Client**

**Your Setup:**
- **Docker Server**: 192.168.1.16 (VM running Docker)
- **Client Device**: 192.168.1.10 (accessing the service)
- **Port**: 5052

## 🚀 **Quick Setup**

### **1. Configure Environment**
```bash
# Edit .env file
echo "SERVER_HOST=192.168.1.16" > .env
echo "SERVER_PORT=5052" >> .env
```

### **2. Start Service**
```bash
./start.sh
```

### **3. Access from Client (192.168.1.10)**
```
http://192.168.1.16:5052/
```

## 🔧 **Detailed Configuration**

### **Environment Variables (.env file)**
```bash
# Server Configuration
SERVER_HOST=192.168.1.16  # Your VM IP address
SERVER_PORT=5052          # Port for the service

# Optional: For different network setups
# SERVER_HOST=0.0.0.0     # Listen on all interfaces
# SERVER_PORT=8080        # Alternative port
```

### **Access URLs**
```bash
# Homepage (interactive interface)
http://192.168.1.16:5052/

# M3U Playlist (for IPTV apps)
http://192.168.1.16:5052/playlist.php

# Individual stream
http://192.168.1.16:5052/stream.php?id=0-9-zeetamil

# JSON API
http://192.168.1.16:5052/get-stream-url.php?id=0-9-zeetamil

# Debug tools
http://192.168.1.16:5052/debug-stream.php
```

## 🎬 **VLC Streaming Fix**

### **VLC Error Solution**
The "Your input can't be opened" error is now fixed with:

#### **1. Enhanced Stream Detection**
- Automatically detects VLC user agent
- Returns plain text URLs for media players
- Improved URL formatting

#### **2. Get VLC-Compatible URLs**
**Method A: Homepage**
1. Visit `http://192.168.1.16:5052/`
2. Click "Get M3U8" on any channel
3. Copy URL and paste in VLC

**Method B: Direct API**
```bash
curl "http://192.168.1.16:5052/get-stream-url.php?id=0-9-zeetamil" | jq -r '.stream_url'
```

**Method C: VLC Direct**
```bash
curl -H "User-Agent: VLC/3.0.18 LibVLC/3.0.18" "http://192.168.1.16:5052/stream.php?id=0-9-zeetamil"
```

## 🔍 **Search Functionality**

### **Features Added**
- **Live search** as you type in the search box
- **Filter channels** by name, genre, language, or ID
- **URL persistence** - search terms saved in URL
- **Clear search** option to reset

### **Search Examples**
```
# Search by language
http://192.168.1.16:5052/?search=tamil

# Search by genre  
http://192.168.1.16:5052/?search=entertainment

# Search by channel name
http://192.168.1.16:5052/?search=zee
```

## 📱 **Client Device Setup**

### **For IPTV Apps (Tivimate, OTT Navigator)**
```
Playlist URL: http://192.168.1.16:5052/playlist.php
```

### **For VLC Mobile**
```
Network Stream: http://192.168.1.16:5052/playlist.php
```

### **For Web Browsers**
```
Homepage: http://192.168.1.16:5052/
```

## 🔧 **Network Troubleshooting**

### **Test Connectivity**
```bash
# From client device (192.168.1.10)
curl -I http://192.168.1.16:5052/

# Should return: HTTP/1.1 200 OK
```

### **Test Playlist**
```bash
curl http://192.168.1.16:5052/playlist.php | head -10
```

### **Test Individual Stream**
```bash
curl -s http://192.168.1.16:5052/get-stream-url.php?id=0-9-zeetamil | jq .
```

### **Check Docker Status**
```bash
docker-compose ps
docker-compose logs -f zee5-app
```

## 🎯 **Port Configuration**

### **Change Default Port**
```bash
# Edit .env file
SERVER_PORT=8080

# Restart service
./stop.sh && ./start.sh
```

### **Firewall Settings**
```bash
# Ubuntu/Debian
sudo ufw allow 5052

# CentOS/RHEL  
sudo firewall-cmd --add-port=5052/tcp --permanent
sudo firewall-cmd --reload
```

## 📊 **Server Status**

### **Environment Info Display**
The homepage now shows:
- **Current server configuration**
- **Base URL for access**
- **Network access instructions**

### **Cookie Status**
- **Real-time authentication status**
- **Expiry time and remaining hours**  
- **Auto-renewal notifications**

## 🎉 **Success Verification**

### **✅ Working Indicators**
- Homepage loads with server IP displayed
- Search functionality filters channels
- M3U8 URLs generate with correct server IP
- VLC can access stream URLs
- Network clients can access service

### **🌐 Network Access Confirmed**
```bash
# From 192.168.1.10:
curl http://192.168.1.16:5052/ | grep "Server Configuration"

# Should show: Base URL: http://192.168.1.16:5052
```

## 🚀 **Advanced Configuration**

### **Multiple Network Interfaces**
```bash
# Listen on all interfaces
SERVER_HOST=0.0.0.0

# Specific interface only
SERVER_HOST=192.168.1.16
```

### **Custom Domain**
```bash
# If you have a local domain
SERVER_HOST=zee5.local.domain
```

### **Load Balancing**
```bash
# Different ports for multiple instances
SERVER_PORT=5052  # Instance 1
SERVER_PORT=5053  # Instance 2
```

Your ZEE5 streaming server is now fully configured for network deployment with VLC streaming fixes, search functionality, and flexible environment configuration! 🎬🌐