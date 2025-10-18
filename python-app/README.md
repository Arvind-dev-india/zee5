# ZEE5 Streaming Service - Python Edition

<div align="center">

  <h3>🐍 Modern Python FastAPI Implementation</h3>
  <p>Complete rewrite with IPTV support, cookie pool management, and auto-refresh</p>

  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
  [![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
  [![License](https://img.shields.io/badge/License-GPL-blue.svg)](LICENSE)

</div>

---

## ✨ Features

### 🎯 Core Features
- ✅ **90+ ZEE5 Live TV Channels** - Complete channel lineup
- ✅ **IPTV Ready** - Works with VLC, Tivimate, OTT Navigator, Kodi
- ✅ **Cookie Pool Management** - Multiple cookies with auto-rotation
- ✅ **Auto-Refresh** - Background cookie refresh (no manual intervention)
- ✅ **Redis Caching** - High-performance caching with file fallback
- ✅ **Playwright Integration** - Browser automation for cookie extraction
- ✅ **Docker Support** - One-command deployment

### 🚀 Technical Improvements
- ⚡ **Async/Await** - Non-blocking I/O for better performance
- 🔄 **Background Tasks** - Automatic cookie refresh and cache cleanup
- 📊 **Health Monitoring** - Built-in health checks and status endpoints
- 🐛 **Debug Tools** - Comprehensive debug page for troubleshooting
- 📝 **API Documentation** - Auto-generated Swagger/OpenAPI docs
- 🔒 **Type Safety** - Full type hints with Pydantic validation

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
cd python-app

# Copy environment file
cp .env.example .env

# Start services
./scripts/start.sh

# Access the service
open http://localhost:5052
```

### Option 2: Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy environment file
cp .env.example .env

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 5052
```

---

## 📋 Requirements

### System Requirements
- Python 3.11+
- Redis (optional, file cache used as fallback)
- Docker & Docker Compose (for containerized deployment)

### Python Dependencies
- FastAPI - Web framework
- Uvicorn - ASGI server
- Playwright - Browser automation
- httpx - Async HTTP client
- Redis - Caching
- Pydantic - Data validation

---

## 🎬 Usage

### 📺 IPTV Playlist

**For VLC, Tivimate, OTT Navigator:**
```
http://localhost:5052/playlist.m3u
```

**For network devices:**
```
http://YOUR_IP:5052/playlist.m3u
```

### 🌐 Web Interface

- **Homepage**: `http://localhost:5052/` - Channel list with search
- **Debug Page**: `http://localhost:5052/debug` - Cookie status and testing
- **API Docs**: `http://localhost:5052/docs` - Interactive API documentation

### 🔗 API Endpoints

```bash
# Health check
GET /health

# Get stream URL (redirect)
GET /stream?id=0-9-zeetv

# Get stream URL (JSON)
GET /get-stream-url?id=0-9-zeetv

# M3U playlist
GET /playlist.m3u

# Cookie management
GET /cookie/status
POST /cookie/refresh

# Channel list
GET /channels?search=news&genre=News
```

---

## ⚙️ Configuration

Edit `.env` file:

```bash
# Server
HOST=0.0.0.0
PORT=5052
SERVER_URL=http://localhost:5052

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
USE_REDIS=true

# Cookie Pool
COOKIE_POOL_SIZE=3              # Number of cookies in pool
COOKIE_REFRESH_INTERVAL=36000   # Refresh every 10 hours
COOKIE_MIN_REMAINING=3600       # Min 1 hour before refresh

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│  IPTV Player    │
│  (VLC/Tivimate) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     Cookie Manager (Pool)         │ │
│  │  - Auto-refresh background task   │ │
│  │  - Playwright browser automation  │ │
│  │  - Redis + file cache             │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     Service Layer                 │ │
│  │  - Stream service                 │ │
│  │  - Channel service                │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     API Routes                    │ │
│  │  - Stream endpoints               │ │
│  │  - M3U playlist                   │ │
│  │  - Admin/debug                    │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Common Issues

**1. IPTV not working**
- Check cookie pool status at `/debug`
- Ensure cookies are valid (green status)
- Try manual refresh: `POST /cookie/refresh`

**2. Geo-restriction errors**
- Service requires India IP address
- Use VPN with Indian server
- Check logs: `docker-compose logs zee5-app`

**3. Redis connection failed**
- Service falls back to file cache automatically
- Check Redis: `docker-compose logs redis`
- Verify `USE_REDIS=true` in `.env`

**4. Playwright errors**
- Ensure Chromium installed: `playwright install chromium`
- Check headless mode: `PLAYWRIGHT_HEADLESS=true`
- View browser logs in debug mode

### Debug Commands

```bash
# View live logs
docker-compose -f docker/docker-compose.yml logs -f

# Check service health
curl http://localhost:5052/health

# Check cookie status
curl http://localhost:5052/cookie/status

# Manual cookie refresh
curl -X POST http://localhost:5052/cookie/refresh

# Restart services
./scripts/stop.sh && ./scripts/start.sh
```

---

## 📊 Performance

- **Startup Time**: ~20-30 seconds
- **Cookie Generation**: ~10-15 seconds per cookie
- **Request Latency**: <100ms (with Redis cache)
- **Concurrent Users**: 100+ (with cookie pool)
- **Memory Usage**: ~200-300 MB
- **CPU Usage**: <5% idle, ~20% during cookie refresh

---

## 🔄 Migration from PHP

### Key Differences

| Feature | PHP Version | Python Version |
|---------|------------|----------------|
| Cookie Management | Per-user (UA hash) | Shared pool |
| Auto-refresh | ❌ Manual | ✅ Automatic |
| Caching | File only | Redis + File |
| IPTV Support | Partial | Full |
| Background Tasks | ❌ None | ✅ Multiple |
| API Docs | ❌ None | ✅ Swagger |
| Type Safety | ❌ None | ✅ Pydantic |

### Migration Steps

1. **Backup PHP data**: Copy `data.json` (already done)
2. **Deploy Python version**: Use Docker or manual setup
3. **Test IPTV players**: Verify playlist works
4. **Monitor**: Check `/debug` page regularly
5. **Switch**: Update DNS/reverse proxy

---

## 🐳 Docker

### Build & Run

```bash
# Build image
docker build -f docker/Dockerfile -t zee5-streaming .

# Run with Docker Compose
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop
docker-compose -f docker/docker-compose.yml down
```

### Environment Variables

```bash
# Set custom port
PORT=8080 docker-compose up -d

# Set server URL for network access
SERVER_URL=http://192.168.1.100:5052 docker-compose up -d

# Enable debug mode
DEBUG=true LOG_LEVEL=DEBUG docker-compose up -d
```

---

## 📝 Development

### Project Structure

```
python-app/
├── app/
│   ├── core/           # Core services (cookie, cache, playwright)
│   ├── api/            # API routes
│   ├── services/       # Business logic
│   ├── templates/      # HTML templates
│   ├── static/         # Static files
│   ├── utils/          # Utilities
│   ├── config.py       # Configuration
│   ├── models.py       # Pydantic models
│   └── main.py         # FastAPI app
├── data/
│   ├── channels.json   # Channel data
│   └── cache/          # File cache
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── start.sh
│   └── stop.sh
├── tests/              # Unit tests
├── requirements.txt
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. The code demonstrates:
- Modern Python async programming
- FastAPI best practices
- Cookie management and browser automation
- IPTV streaming protocols
- Docker containerization

**Not responsible for misuse or revenue loss to content providers.**

---

## 📜 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

- **Original PHP Version**: [@yuvraj824](https://github.com/yuvraj824)
- **Python Rewrite**: Enhanced with modern architecture and IPTV support
- **Community**: [Telegram Channel](https://t.me/ygxworld) | [Telegram Chat](https://t.me/ygx_chat)

---

<div align="center">

  **⭐ Star this repo if you found it helpful!**

  Made with ❤️ for the community

</div>
