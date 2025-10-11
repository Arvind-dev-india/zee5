# 🔧 ZEE5 Streaming Troubleshooting Guide

## 🎯 Current Status

✅ **Docker Setup**: Working perfectly  
✅ **Cookie Generation**: Working (cached for 12 hours)  
✅ **Stream URL Generation**: Working  
❌ **Actual Streaming**: Getting HTTP 403 Forbidden  

## 🐛 Common Issues & Solutions

### 1. 🌍 **Geo-Restriction Issues**
**Problem**: HTTP 403 Forbidden when accessing stream URLs  
**Causes**:
- Server IP is outside India
- VPN detection by ZEE5
- IP blocking by content provider

**Solutions**:
- Use a VPN with Indian IP
- Try different server locations
- Use proxy servers in India

### 2. 🔐 **Authentication Issues**
**Problem**: Cookies not working or expired  
**Check**: Visit `http://localhost:5052/debug-stream.php`  
**Solutions**:
- Clear cookie cache: `rm tmp/cookie_z5_*.tmp`
- Restart the service: `./stop.sh && ./start.sh`
- Check authentication status on homepage

### 3. 🌐 **User Agent Issues**  
**Current User Agent**: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36`  
**VLC User Agent**: `VLC/3.0.18 LibVLC/3.0.18`

**Testing Different User Agents**:
```bash
# Test with Chrome user agent
curl -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" "http://localhost:5052/stream.php?id=0-9-zeetamil"

# Test with VLC user agent  
curl -H "User-Agent: VLC/3.0.18 LibVLC/3.0.18" "http://localhost:5052/stream.php?id=0-9-zeetamil"
```

### 4. 📺 **VLC Player Issues**
**For VLC Users**:
1. Copy the M3U8 URL from the homepage "Get M3U8" button
2. Open VLC → Media → Open Network Stream
3. Paste the complete URL (including authentication parameters)
4. Make sure VLC network settings allow HTTP streams

**VLC Network Settings**:
- Tools → Preferences → Show All → Input/Codecs → Access modules → HTTP
- Disable "Use HTTP authentication" if enabled
- Set User Agent to match browser if needed

### 5. 🔄 **IPTV App Issues**
**M3U Playlist URL**: `http://localhost:5052/playlist.php`

**Common IPTV App Settings**:
- **Tivimate**: Add as "M3U Playlist", use full URL
- **VLC Mobile**: Network Stream, paste M3U URL
- **OTT Navigator**: Add playlist, use HTTP URL

## 🧪 **Testing Commands**

### Test Homepage
```bash
curl http://localhost:5052/
```

### Test Playlist
```bash  
curl http://localhost:5052/playlist.php
```

### Test Stream API
```bash
curl http://localhost:5052/get-stream-url.php?id=0-9-zeetamil
```

### Test Debug Page
```bash
curl http://localhost:5052/debug-stream.php
```

### Check Container Logs
```bash
docker-compose logs -f zee5-app
```

## 🔧 **Manual Testing**

### 1. Get Stream URL Manually
```bash
STREAM_URL=$(curl -s "http://localhost:5052/get-stream-url.php?id=0-9-zeetamil" | jq -r '.stream_url')
echo $STREAM_URL
```

### 2. Test Stream URL Directly
```bash
curl -I "$STREAM_URL"
```

### 3. Test with Different User Agents
```bash
curl -I -H "User-Agent: VLC/3.0.18 LibVLC/3.0.18" "$STREAM_URL"
```

## 🌐 **Network Access Issues**

### From Other Devices
Replace `localhost` with your computer's IP:
```bash
# Find your IP
ip addr show | grep inet

# Use your IP instead of localhost
http://192.168.1.100:5052/playlist.php
```

### Port Issues
If port 5052 is blocked:
1. Edit `docker-compose.yml`
2. Change `"5052:80"` to `"8080:80"` or another port
3. Restart: `docker-compose down && docker-compose up -d`

## 🎯 **Working Alternatives**

### 1. Use Homepage Interface
- Visit `http://localhost:5052/`
- Click "Get M3U8" for individual channels
- Copy the generated URL to VLC

### 2. Use Playlist Method
- Use `http://localhost:5052/playlist.php` in IPTV apps
- This generates a complete M3U playlist with all channels

### 3. Debug Individual Channels
- Use `http://localhost:5052/debug-stream.php?id=CHANNEL_ID`
- This shows detailed information about stream generation

## ⚠️ **Known Limitations**

1. **Geo-Restrictions**: ZEE5 content is restricted to India
2. **IP Blocking**: Some server IPs may be blocked
3. **Rate Limiting**: Too many requests may trigger blocks
4. **Authentication**: Cookies expire every 12 hours
5. **Network**: Some firewalls block streaming protocols

## 🎉 **Success Indicators**

✅ Homepage loads with all channels  
✅ Cookie status shows "Active" with expiry time  
✅ M3U8 URLs generate successfully  
✅ Stream URLs return HTTP 200 or proper redirects  
✅ VLC can play the stream URLs  

## 📞 **Getting Help**

If streaming still doesn't work:
1. Check if you're accessing from India or using Indian VPN
2. Try different channels (some may work better than others)
3. Use the debug page to identify specific issues
4. Check Docker logs for error messages
5. Test with different IPTV applications