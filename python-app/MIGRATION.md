# Migration Guide: PHP to Python

## 🔄 Migration Overview

This guide helps you migrate from the PHP version to the Python FastAPI version.

---

## 📊 Feature Comparison

| Feature | PHP Version | Python Version | Status |
|---------|------------|----------------|--------|
| **Core Streaming** | ✅ | ✅ | Improved |
| **Cookie Management** | Per-user (UA hash) | Shared pool | ✅ Better |
| **Auto-refresh** | ❌ Manual | ✅ Automatic | ✅ New |
| **Caching** | File only | Redis + File | ✅ Better |
| **IPTV Support** | Partial | Full | ✅ Fixed |
| **Background Tasks** | ❌ | ✅ Multiple | ✅ New |
| **API Documentation** | ❌ | ✅ Swagger | ✅ New |
| **Type Safety** | ❌ | ✅ Pydantic | ✅ New |
| **Performance** | Good | Excellent | ✅ Better |
| **Memory Usage** | ~50-100 MB | ~200-300 MB | ⚠️ Higher |
| **Setup Complexity** | Simple | Moderate | ⚠️ More complex |

---

## 🚀 Migration Steps

### Step 1: Backup Current Setup

```bash
# Backup PHP files
cd /path/to/php/version
tar -czf zee5-php-backup-$(date +%Y%m%d).tar.gz .

# Backup data
cp data.json ~/zee5-data-backup.json
```

### Step 2: Deploy Python Version

**Option A: Docker (Recommended)**
```bash
cd python-app
cp .env.example .env
# Edit .env with your configuration
./scripts/start.sh
```

**Option B: Manual**
```bash
cd python-app
./scripts/setup-dev.sh
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 5052
```

### Step 3: Verify Functionality

1. **Check Health**
   ```bash
   curl http://localhost:5052/health
   ```

2. **Test Stream**
   ```bash
   curl http://localhost:5052/stream?id=0-9-zeetv
   ```

3. **Test Playlist**
   ```bash
   curl http://localhost:5052/playlist.m3u
   ```

4. **Check Cookie Pool**
   ```bash
   curl http://localhost:5052/cookie/status
   ```

### Step 4: Update IPTV Players

**Old URL:**
```
http://your-server:5052/playlist.php
```

**New URL:**
```
http://your-server:5052/playlist.m3u
```

**Note**: Both `/playlist.m3u` and `/playlist.php` work (backward compatible)

### Step 5: Monitor & Optimize

1. **Check Logs**
   ```bash
   docker-compose -f docker/docker-compose.yml logs -f zee5-app
   ```

2. **Monitor Cookie Status**
   - Visit: `http://your-server:5052/debug`
   - Check cookie pool health

3. **Optimize Configuration**
   - Adjust `COOKIE_POOL_SIZE` based on load
   - Enable Redis for better performance
   - Set appropriate `LOG_LEVEL`

---

## 🔑 Key Differences

### 1. Cookie Management

**PHP (Old)**:
- One cookie per user-agent
- File cache only
- Manual refresh needed
- Cache key: `md5(user_agent)`

**Python (New)**:
- Shared cookie pool (3-5 cookies)
- Redis + file cache
- Automatic background refresh
- Distributed across all users

### 2. URL Structure

**Mostly Compatible** - No changes needed for most use cases

| Endpoint | PHP | Python | Compatible |
|----------|-----|--------|------------|
| Playlist | `/playlist.php` | `/playlist.m3u` or `/playlist.php` | ✅ Yes |
| Stream | `/stream.php?id=X` | `/stream?id=X` | ⚠️ Minor |
| Get URL | `/get-stream-url.php?id=X` | `/get-stream-url?id=X` | ⚠️ Minor |

### 3. Environment Variables

**PHP (.env)**:
```bash
SERVER_HOST=192.168.1.16
SERVER_PORT=5052
```

**Python (.env)**:
```bash
HOST=0.0.0.0
PORT=5052
SERVER_URL=http://192.168.1.16:5052
REDIS_HOST=localhost
COOKIE_POOL_SIZE=3
```

---

## ⚠️ Breaking Changes

### 1. Stream URL Response

**PHP**: Always redirects (302)
**Python**:
- Redirects for browsers (302)
- Returns plain text for media players
- Can specify format: `?format=url`

### 2. Cache Structure

**PHP**: Individual cache files per UA
**Python**: Shared cache in Redis/file

**Migration**: Old cache files won't work, new cookies will be generated

### 3. Error Responses

**PHP**: Plain text errors
**Python**: JSON error responses

```json
{
  "error": "Channel not found",
  "detail": "Channel ID 'invalid' does not exist",
  "timestamp": "2025-01-15T10:30:45"
}
```

---

## 🐛 Troubleshooting Migration

### Issue 1: IPTV Players Not Working

**Symptom**: Playlist loads but streams don't play

**Solutions**:
1. Check cookie pool status: `/cookie/status`
2. Verify Redis is running: `docker ps | grep redis`
3. Try manual cookie refresh: `POST /cookie/refresh`
4. Check server URL in `.env`: `SERVER_URL=http://YOUR_IP:5052`

### Issue 2: High Memory Usage

**Symptom**: Python version uses more RAM than PHP

**Solutions**:
1. Reduce cookie pool size: `COOKIE_POOL_SIZE=2`
2. Disable Redis (use file cache): `USE_REDIS=false`
3. Lower Playwright instances
4. Add swap memory if needed

### Issue 3: Slow Startup

**Symptom**: Service takes 30+ seconds to start

**This is normal**:
- Playwright browser launch: ~10s
- Cookie pool initialization: ~15s per cookie
- Channel data loading: ~2s

**To speed up**:
1. Use smaller cookie pool initially
2. Pre-cache cookies before deployment
3. Use Redis for faster cache access

### Issue 4: Geo-restriction Errors

**Same as PHP version** - Requires India IP

**Solutions**:
1. Use VPN with Indian server
2. Deploy on Indian VPS
3. Use proxy rotation (advanced)

---

## 📈 Performance Tuning

### For Low-Resource Servers

```bash
# .env configuration
COOKIE_POOL_SIZE=2              # Reduce pool
USE_REDIS=false                 # Skip Redis
PLAYWRIGHT_HEADLESS=true        # Always headless
LOG_LEVEL=WARNING               # Less logging
```

### For High-Traffic Servers

```bash
# .env configuration
COOKIE_POOL_SIZE=5              # Larger pool
USE_REDIS=true                  # Enable Redis
REDIS_HOST=redis-server         # Dedicated Redis
COOKIE_REFRESH_INTERVAL=28800   # 8 hours
```

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  zee5-app:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

---

## 🔄 Rollback Plan

If you need to rollback to PHP:

1. **Stop Python version**:
   ```bash
   cd python-app
   ./scripts/stop.sh
   ```

2. **Restore PHP version**:
   ```bash
   cd /path/to/php
   docker-compose up -d
   # or
   # Start Apache/PHP server
   ```

3. **Update IPTV URLs** back to:
   ```
   http://your-server:5052/playlist.php
   ```

4. **Restore data** (if needed):
   ```bash
   cp ~/zee5-data-backup.json data.json
   ```

---

## ✅ Post-Migration Checklist

- [ ] Python service running and healthy
- [ ] Cookie pool has valid cookies
- [ ] Test stream in VLC player
- [ ] Test IPTV playlist in Tivimate
- [ ] Monitor logs for errors
- [ ] Update documentation/bookmarks
- [ ] Backup configuration files
- [ ] Set up monitoring/alerts
- [ ] Test on multiple devices
- [ ] Verify network access from other devices

---

## 🆘 Getting Help

**Issues with Migration**:
1. Check logs: `docker-compose logs zee5-app`
2. Visit debug page: `http://localhost:5052/debug`
3. Check health: `http://localhost:5052/health`
4. Review [ARCHITECTURE.md](ARCHITECTURE.md)

**Community Support**:
- Telegram: https://t.me/ygxworld
- GitHub Issues: Create detailed issue with logs

---

## 📝 Migration Timeline

**Recommended Timeline**:

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Week 1** | Preparation | Setup Python environment, test locally |
| **Week 2** | Testing | Deploy side-by-side, test all features |
| **Week 3** | Migration | Switch production traffic, monitor |
| **Week 4** | Optimization | Fine-tune performance, cleanup |

---

## 🎉 Migration Complete!

Once migration is successful:

1. ✅ Remove old PHP files (after backup)
2. ✅ Update documentation
3. ✅ Monitor for 1-2 weeks
4. ✅ Optimize based on usage patterns

**Congratulations on upgrading to the Python version!** 🐍

---

**Last Updated**: 2025-01-15
**Migration Version**: PHP → Python 2.0
