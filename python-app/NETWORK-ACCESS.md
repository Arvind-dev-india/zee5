# Network Access Guide

## 🌐 Accessing ZEE5 Streaming Service from Other Devices

This guide helps you configure the service for network access from other devices (phones, tablets, other computers, IPTV players).

---

## 🚀 Quick Setup

### Step 1: Find Your Server IP

Run the network setup helper:
```bash
cd python-app
./scripts/network-setup.sh
```

Or manually find your IP:

**Linux/Mac:**
```bash
# Show all IPs
ip addr show | grep "inet " | grep -v 127.0.0.1

# Or
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```cmd
ipconfig | findstr IPv4
```

Example output: `192.168.1.100`

---

### Step 2: Update Configuration

Edit `.env` file:
```bash
# Change this line:
SERVER_URL=http://localhost:5052

# To your server IP:
SERVER_URL=http://192.168.1.100:5052
```

Or use environment variable:
```bash
export SERVER_URL=http://192.168.1.100:5052
docker-compose up -d
```

---

### Step 3: Restart Service

```bash
./scripts/stop.sh
./scripts/start.sh
```

Or:
```bash
cd docker
docker-compose down
docker-compose up -d
```

---

## 📱 Accessing from Devices

### On Same Network (LAN)

**Playlist URL:**
```
http://192.168.1.100:5052/playlist.m3u
```

**Homepage:**
```
http://192.168.1.100:5052/
```

**Replace** `192.168.1.100` with your actual server IP.

---

## 🔥 Firewall Configuration

### Ubuntu/Debian

```bash
# Allow port 5052
sudo ufw allow 5052/tcp

# Check status
sudo ufw status
```

### CentOS/RHEL/Fedora

```bash
# Allow port 5052
sudo firewall-cmd --permanent --add-port=5052/tcp
sudo firewall-cmd --reload

# Check status
sudo firewall-cmd --list-ports
```

### Docker (Already Configured)

The docker-compose.yml already binds to `0.0.0.0:5052` which makes it accessible from all network interfaces.

---

## 📺 IPTV Player Setup

### VLC Player

1. Open VLC
2. Media → Open Network Stream
3. Enter URL: `http://192.168.1.100:5052/playlist.m3u`
4. Click Play

### Tivimate

1. Open Tivimate
2. Settings → Playlists
3. Add Playlist
4. Select "URL"
5. Enter: `http://192.168.1.100:5052/playlist.m3u`
6. Give it a name: "ZEE5"
7. Save

### OTT Navigator

1. Open OTT Navigator
2. Add Playlist
3. Playlist Type: M3U URL
4. Enter: `http://192.168.1.100:5052/playlist.m3u`
5. Save

### Kodi

1. Install "PVR IPTV Simple Client" addon
2. Configure addon
3. M3U Play List URL: `http://192.168.1.100:5052/playlist.m3u`
4. Enable addon
5. Restart Kodi

---

## 🌍 Public Internet Access

### Option 1: Port Forwarding (Router)

1. **Login to your router** (usually 192.168.1.1)
2. **Find Port Forwarding** section
3. **Add new rule**:
   - External Port: 5052
   - Internal IP: Your server IP (192.168.1.100)
   - Internal Port: 5052
   - Protocol: TCP
4. **Save** and test with your public IP

**Playlist URL:**
```
http://YOUR_PUBLIC_IP:5052/playlist.m3u
```

⚠️ **Security Warning**: Only do this if you understand the security implications.

### Option 2: Reverse Proxy (Nginx)

**Install Nginx:**
```bash
sudo apt-get install nginx
```

**Configure Nginx** (`/etc/nginx/sites-available/zee5`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5052;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Enable and restart:**
```bash
sudo ln -s /etc/nginx/sites-available/zee5 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Access via:**
```
http://your-domain.com/playlist.m3u
```

### Option 3: Cloudflare Tunnel (Recommended)

**Install cloudflared:**
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

**Create tunnel:**
```bash
cloudflared tunnel login
cloudflared tunnel create zee5
cloudflared tunnel route dns zee5 zee5.your-domain.com
```

**Configure** (`~/.cloudflared/config.yml`):
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/user/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: zee5.your-domain.com
    service: http://localhost:5052
  - service: http_status:404
```

**Run tunnel:**
```bash
cloudflared tunnel run zee5
```

**Access via:**
```
https://zee5.your-domain.com/playlist.m3u
```

---

## 🧪 Testing Network Access

### From Another Device

**Test 1: Check if port is accessible**
```bash
# From another device on same network
telnet 192.168.1.100 5052
# Should connect successfully
```

**Test 2: Check service health**
```bash
curl http://192.168.1.100:5052/health
# Should return JSON with status
```

**Test 3: Get playlist**
```bash
curl http://192.168.1.100:5052/playlist.m3u
# Should return M3U playlist
```

---

## 🐛 Troubleshooting

### Can't Connect from Other Devices

**Issue**: Connection refused or timeout

**Solutions**:
1. **Check firewall**:
   ```bash
   sudo ufw status
   # Make sure 5052 is allowed
   ```

2. **Verify service is running**:
   ```bash
   docker ps | grep zee5
   # Should show container running
   ```

3. **Check if listening on all interfaces**:
   ```bash
   sudo netstat -tulpn | grep 5052
   # Should show 0.0.0.0:5052
   ```

4. **Test from server itself**:
   ```bash
   curl http://localhost:5052/health
   # Should work
   ```

5. **Check SERVER_URL in .env**:
   ```bash
   cat .env | grep SERVER_URL
   # Should be your actual IP, not localhost
   ```

### Playlist Loads But Streams Don't Play

**Issue**: IPTV player shows channels but won't play

**Solutions**:
1. **Update SERVER_URL** in .env to your actual IP
2. **Restart service** after changing .env
3. **Check cookie pool**:
   ```bash
   curl http://192.168.1.100:5052/cookie/status
   # Should show valid cookies
   ```

### Slow Streaming

**Issue**: Buffering or slow playback

**Solutions**:
1. **Check network bandwidth**
2. **Reduce concurrent streams**
3. **Use wired connection instead of WiFi**
4. **Check server CPU/memory usage**

---

## 📊 Performance Tips

### For Better Network Performance

1. **Use wired connection** for server
2. **Enable QoS** on router for streaming traffic
3. **Increase cookie pool size** for more concurrent users:
   ```bash
   # In .env
   COOKIE_POOL_SIZE=5
   ```
4. **Use Redis** for better caching:
   ```bash
   USE_REDIS=true
   ```

---

## ✅ Network Access Checklist

- [ ] Found server IP address
- [ ] Updated SERVER_URL in .env
- [ ] Restarted service
- [ ] Opened port 5052 in firewall
- [ ] Tested from another device on same network
- [ ] Playlist loads in VLC
- [ ] Streams play successfully
- [ ] Updated IPTV player with new URL

---

## 🆘 Still Having Issues?

1. Check logs:
   ```bash
   docker-compose -f docker/docker-compose.yml logs -f zee5-app
   ```

2. Visit debug page:
   ```
   http://YOUR_IP:5052/debug
   ```

3. Check health endpoint:
   ```
   http://YOUR_IP:5052/health
   ```

---

**Network access configured!** 🎉

Your ZEE5 streaming service is now accessible from all devices on your network (and optionally from the internet if you set up port forwarding or reverse proxy).
