# ZEE5 Streaming Service - Docker Setup

## 🐳 Complete Docker Setup for IPTV Streaming

This directory contains a **production-ready Docker setup** for the ZEE5 Streaming Service.

---

## ⚡ Quick Start (3 Commands)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start services
./start.sh

# 3. Access the service
# Open http://localhost:5052
```

**That's it!** The service is now running with:
- ✅ Python FastAPI application
- ✅ Redis caching
- ✅ Playwright browser automation
- ✅ Auto-refreshing cookie pool
- ✅ 90+ live TV channels

---

## 📋 What's Included

### Services
- **zee5-app**: Python FastAPI streaming service (Port 5052)
- **redis**: Redis cache for cookie storage (Port 6379, localhost only)

### Features
- Docker Compose orchestration
- Automatic container restart
- Health checks
- Volume persistence
- Network isolation
- Production-ready configuration

---

## 🚀 Usage

### Start Service
```bash
./start.sh
```

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

### Restart Service
```bash
./stop.sh && ./start.sh
```

---

## 🌐 Access Points

### Local Access
- **Homepage**: http://localhost:5052/
- **M3U Playlist**: http://localhost:5052/playlist.m3u
- **Debug Page**: http://localhost:5052/debug
- **Health Check**: http://localhost:5052/health
- **API Docs**: http://localhost:5052/docs

### Network Access (from other devices)

1. **Find your server IP**:
   ```bash
   ip addr show | grep "inet " | grep -v 127.0.0.1
   # Example: 192.168.1.100
   ```

2. **Update .env file**:
   ```bash
   # Change this line:
   SERVER_URL=http://localhost:5052

   # To your IP:
   SERVER_URL=http://192.168.1.100:5052
   ```

3. **Restart service**:
   ```bash
   ./stop.sh && ./start.sh
   ```

4. **Access from any device**:
   - Playlist: http://192.168.1.100:5052/playlist.m3u
   - Homepage: http://192.168.1.100:5052/

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Server URL (IMPORTANT for network access)
SERVER_URL=http://192.168.1.100:5052

# Cookie Pool Configuration
COOKIE_POOL_SIZE=3              # Number of cookies in pool
COOKIE_REFRESH_INTERVAL=36000   # Refresh every 10 hours (seconds)
COOKIE_MIN_REMAINING=3600       # Start refresh when <1 hour remains

# Logging
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
DEBUG=false                     # Enable debug mode
```

### Docker Compose Customization

Edit `docker-compose.yml` to customize:
- Port mappings
- Resource limits
- Volume mounts
- Environment variables

---

## 📊 Monitoring

### Check Service Status
```bash
docker-compose ps
```

### Check Health
```bash
curl http://localhost:5052/health
```

### Cookie Pool Status
```bash
curl http://localhost:5052/cookie/status
```

### Container Stats
```bash
docker stats zee5-streaming zee5-redis
```

---

## 🐛 Troubleshooting

### Service won't start

**Check logs**:
```bash
docker-compose logs zee5-app
```

**Rebuild containers**:
```bash
docker-compose down
docker-compose up -d --build
```

### Can't access from other devices

**Check firewall**:
```bash
# Ubuntu/Debian
sudo ufw allow 5052/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5052/tcp
sudo firewall-cmd --reload
```

**Verify port binding**:
```bash
docker-compose ps
# zee5-app should show 0.0.0.0:5052->5052/tcp
```

**Check SERVER_URL**:
```bash
cat .env | grep SERVER_URL
# Should be your actual IP, not localhost
```

### IPTV not working

**Check cookie pool**:
```bash
curl http://localhost:5052/cookie/status
```

**Refresh cookies manually**:
```bash
curl -X POST http://localhost:5052/cookie/refresh
```

**View debug page**:
```
http://localhost:5052/debug
```

---

## 🔥 Advanced Usage

### Resource Limits

Add to `docker-compose.yml` under `zee5-app`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      cpus: '1'
      memory: 512M
```

### Custom Playwright Settings

Add to environment in `docker-compose.yml`:
```yaml
environment:
  - PLAYWRIGHT_HEADLESS=true
  - PLAYWRIGHT_TIMEOUT=60000
```

### Scale Containers

```bash
docker-compose up -d --scale zee5-app=3
```

### Backup Data

```bash
# Backup channel data
docker-compose exec zee5-app cat /app/data/channels.json > backup-channels.json

# Backup Redis data
docker-compose exec redis redis-cli SAVE
docker cp zee5-redis:/data/dump.rdb ./backup-redis-dump.rdb
```

---

## 🗑️ Cleanup

### Stop and remove containers
```bash
docker-compose down
```

### Remove volumes (deletes cached data)
```bash
docker-compose down -v
```

### Remove everything including images
```bash
docker-compose down -v --rmi all
```

---

## 📱 IPTV Player Setup

### VLC
1. Media → Open Network Stream
2. URL: `http://YOUR_IP:5052/playlist.m3u`
3. Play

### Tivimate
1. Settings → Playlists → Add Playlist
2. Select "URL"
3. Enter: `http://YOUR_IP:5052/playlist.m3u`
4. Save

### Kodi
1. Install "PVR IPTV Simple Client"
2. Configure addon
3. M3U URL: `http://YOUR_IP:5052/playlist.m3u`
4. Enable and restart

---

## 📈 Performance Tuning

### For Low Resources
```bash
# .env
COOKIE_POOL_SIZE=2
LOG_LEVEL=WARNING
```

### For High Traffic
```bash
# .env
COOKIE_POOL_SIZE=5
COOKIE_REFRESH_INTERVAL=28800
```

---

## 🔐 Security Notes

1. **Redis** is bound to localhost only (not exposed to network)
2. **Port 5052** is exposed - use firewall rules if needed
3. **No authentication** - add reverse proxy with auth if public
4. **Cookies cached** - automatically expire and refresh

---

## 🆘 Getting Help

**Check Status**:
```bash
./start.sh  # Shows status and URLs
./logs.sh   # View live logs
```

**Visit Debug Page**:
```
http://localhost:5052/debug
```

**Check Health**:
```
http://localhost:5052/health
```

**View Documentation**:
- [README.md](python-app/README.md) - Full documentation
- [ARCHITECTURE.md](python-app/ARCHITECTURE.md) - Technical details
- [NETWORK-ACCESS.md](python-app/NETWORK-ACCESS.md) - Network setup guide

---

## ✅ Quick Reference

| Command | Description |
|---------|-------------|
| `./start.sh` | Start all services |
| `./stop.sh` | Stop all services |
| `./logs.sh` | View live logs |
| `docker-compose ps` | Check status |
| `docker-compose restart` | Restart services |
| `docker-compose down -v` | Remove everything |

---

## 🎉 Success!

Your ZEE5 streaming service is now running in Docker!

**Test it**:
1. Open http://localhost:5052
2. Click on any channel to stream
3. Use playlist URL in your IPTV player

**Questions?** Check the docs in `python-app/` directory.

---

**Docker Setup Complete!** 🐳
