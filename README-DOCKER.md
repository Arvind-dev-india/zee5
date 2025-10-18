# ZEE5 Streaming Service 🎬

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-GPL-blue.svg)](LICENSE)

**Modern Python FastAPI implementation with full IPTV support**

Complete rewrite with cookie pool management, auto-refresh, and Redis caching

</div>

---

## ⚡ Quick Start (3 Commands)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. (Optional) Edit .env to set your server IP
nano .env  # Change SERVER_URL=http://YOUR_IP:5052

# 3. Start with Docker
./start.sh
```

**Access**: http://localhost:5052

**Playlist for IPTV**: http://localhost:5052/playlist.m3u

---

## ✨ Features

### 🎯 Core
- ✅ **90+ ZEE5 Channels** - Complete live TV lineup
- ✅ **IPTV Ready** - Works with VLC, Tivimate, OTT Navigator, Kodi
- ✅ **Cookie Pool** - Multiple cookies with auto-rotation
- ✅ **Auto-Refresh** - Background tasks, no manual intervention
- ✅ **Redis Caching** - High-performance with file fallback
- ✅ **Network Access** - Accessible from all devices on your network

### 🚀 Technical
- ⚡ **Async/Await** - Python FastAPI for better performance
- 🔄 **Background Tasks** - Auto cookie refresh every 10 hours
- 🎭 **Playwright** - Browser automation for cookie extraction
- 📊 **Health Monitoring** - Built-in debug and status endpoints
- 📝 **API Docs** - Auto-generated Swagger documentation
- 🐳 **Docker** - One-command deployment

---

## 🐳 Docker Setup

### Requirements
- Docker
- Docker Compose

### Start Service
```bash
./start.sh
```

This will:
1. Build Python FastAPI application
2. Start Redis cache
3. Install Playwright browsers
4. Initialize cookie pool
5. Start service on port 5052

### Stop Service
```bash
./stop.sh
```

### View Logs
```bash
./logs.sh
# or
docker-compose logs -f zee5-app
```

---

## 🌐 Network Access

### Local Access
```
http://localhost:5052/playlist.m3u
```

### From Other Devices

**1. Find your server IP:**
```bash
./start.sh  # Shows your IP addresses
```

**2. Edit .env file:**
```bash
nano .env

# Change this line:
SERVER_URL=http://192.168.1.16:5052
```

**3. Restart:**
```bash
./stop.sh && ./start.sh
```

**4. Access from any device:**
```
http://192.168.1.16:5052/playlist.m3u
```

---

## 📺 IPTV Player Setup

### VLC
1. Media → Open Network Stream
2. Enter: `http://YOUR_IP:5052/playlist.m3u`
3. Play

### Tivimate
1. Settings → Playlists → Add Playlist
2. Select "URL"
3. Enter: `http://YOUR_IP:5052/playlist.m3u`
4. Save

### OTT Navigator
1. Add Playlist
2. M3U URL: `http://YOUR_IP:5052/playlist.m3u`
3. Save

### Kodi
1. Install "PVR IPTV Simple Client"
2. Configure: M3U URL: `http://YOUR_IP:5052/playlist.m3u`
3. Enable addon

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Server URL (set to your IP for network access)
SERVER_URL=http://192.168.1.16:5052

# Cookie Pool
COOKIE_POOL_SIZE=3              # Number of cookies
COOKIE_REFRESH_INTERVAL=36000   # Refresh every 10 hours
COOKIE_MIN_REMAINING=3600       # Start refresh at 1 hour remaining

# Logging
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
DEBUG=false
```

---

## 📊 Monitoring

### Web Interfaces
- **Homepage**: http://localhost:5052/
- **Debug Page**: http://localhost:5052/debug
- **Health Check**: http://localhost:5052/health
- **API Docs**: http://localhost:5052/docs

### Command Line
```bash
# Service status
docker-compose ps

# Health check
curl http://localhost:5052/health

# Cookie pool status
curl http://localhost:5052/cookie/status

# Container logs
docker-compose logs -f zee5-app
```

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs zee5-app

# Rebuild
docker-compose down
docker-compose up -d --build
```

### Can't access from other devices
```bash
# Check firewall (Ubuntu)
sudo ufw allow 5052/tcp

# Verify SERVER_URL in .env
cat .env | grep SERVER_URL

# Should be your IP, not localhost
```

### IPTV not working
```bash
# Check cookies
curl http://localhost:5052/cookie/status

# Refresh manually
curl -X POST http://localhost:5052/cookie/refresh

# Visit debug page
http://localhost:5052/debug
```

---

## 📖 Documentation

- **[DOCKER-SETUP.md](DOCKER-SETUP.md)** - Complete Docker guide
- **[python-app/README.md](python-app/README.md)** - Full documentation
- **[python-app/ARCHITECTURE.md](python-app/ARCHITECTURE.md)** - Technical details
- **[python-app/NETWORK-ACCESS.md](python-app/NETWORK-ACCESS.md)** - Network setup guide
- **[python-app/MIGRATION.md](python-app/MIGRATION.md)** - PHP to Python migration

---

## 🔄 Updates from PHP Version

| Feature | PHP | Python | Status |
|---------|-----|--------|--------|
| Streaming | ✅ | ✅ | Improved |
| Cookie Management | Per-user | Shared pool | ✅ Better |
| Auto-refresh | ❌ | ✅ | ✅ New |
| Caching | File | Redis + File | ✅ Better |
| IPTV Support | Partial | Full | ✅ Fixed |
| Background Tasks | ❌ | ✅ | ✅ New |
| API Docs | ❌ | ✅ | ✅ New |

---

## 🔥 Firewall (if needed)

**Ubuntu/Debian:**
```bash
sudo ufw allow 5052/tcp
```

**CentOS/RHEL:**
```bash
sudo firewall-cmd --permanent --add-port=5052/tcp
sudo firewall-cmd --reload
```

---

## 🗑️ Cleanup

```bash
# Stop and remove containers
./stop.sh

# Remove all data (Redis cache, cookies)
docker-compose down -v

# Remove images too
docker-compose down -v --rmi all
```

---

## ⚠️ Disclaimer

**For educational purposes only.** This project demonstrates:
- Modern Python async programming
- FastAPI best practices
- Browser automation with Playwright
- IPTV streaming protocols
- Docker containerization

Not responsible for misuse or revenue loss to content providers.

---

## 🙏 Credits

- **Original PHP**: [@yuvraj824](https://github.com/yuvraj824)
- **Python Rewrite**: Enhanced with modern architecture
- **Community**: [Telegram](https://t.me/ygxworld)

---

## 📜 License

GPL-3.0 License - see [LICENSE](LICENSE)

---

<div align="center">

**⭐ Star this repo if helpful!**

Made with ❤️ for the community

</div>
