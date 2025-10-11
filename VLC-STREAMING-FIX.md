# 🎬 VLC Streaming Fix Guide

## 🐛 **VLC Error: "Your input can't be opened"**

### **Root Cause**
The error you're experiencing is typically caused by:
1. **Geo-restrictions** - ZEE5 blocks non-Indian IP addresses
2. **URL formatting** - Special characters in authentication tokens
3. **User agent** - VLC's user agent may be blocked

### 🔧 **Solutions Applied**

#### **1. Enhanced Stream Endpoint**
- **Fixed URL formatting** to prevent character encoding issues
- **Added VLC detection** - returns plain text URL for media players
- **Improved error handling** with better user feedback

#### **2. Network Configuration**
- **Environment variables** for flexible IP/port configuration  
- **Auto-detection** of server IP and port
- **Cross-network compatibility** for VM deployments

#### **3. VLC-Specific Improvements**
```php
// For VLC and other players, return URL directly
if (strpos($userAgentLower, 'vlc') !== false) {
    header('Content-Type: text/plain');
    echo $finalUrl;
    exit;
}
```

### 🎯 **How to Use with VLC**

#### **Method 1: Get M3U8 URL from Homepage**
1. Visit: `http://your-server-ip:5052/`
2. Click "Get M3U8" on any channel
3. Copy the generated URL
4. VLC → Media → Open Network Stream → Paste URL

#### **Method 2: Direct URL Format**
```
http://your-server-ip:5052/stream.php?id=CHANNEL_ID&format=url
```

#### **Method 3: Use Playlist**
```
http://your-server-ip:5052/playlist.php
```

### 🌐 **Network Configuration Setup**

#### **For VM Deployment (192.168.1.16 → 192.168.1.10)**

1. **Edit `.env` file:**
   ```bash
   SERVER_HOST=192.168.1.16
   SERVER_PORT=5052
   ```

2. **Restart service:**
   ```bash
   ./stop.sh && ./start.sh
   ```

3. **Access from client (192.168.1.10):**
   ```
   http://192.168.1.16:5052/
   ```

### 🔍 **Debugging Steps**

#### **1. Test URL Generation**
```bash
curl -s "http://192.168.1.16:5052/get-stream-url.php?id=0-9-zeetamil" | jq .
```

#### **2. Test VLC User Agent**
```bash
curl -H "User-Agent: VLC/3.0.18 LibVLC/3.0.18" "http://192.168.1.16:5052/stream.php?id=0-9-zeetamil"
```

#### **3. Check Debug Page**
```
http://192.168.1.16:5052/debug-stream.php?id=0-9-zeetamil
```

### ⚠️ **Known Limitations**

#### **Geo-Restrictions**
- ZEE5 content is **geo-blocked** outside India
- May require **Indian VPN** for actual streaming
- Authentication works, but stream access may be blocked

#### **VLC Settings**
1. **Tools → Preferences → Show All**
2. **Input/Codecs → Access modules → HTTP**
3. **Disable "Use HTTP authentication"**
4. **Set custom User-Agent** if needed

### 🎉 **Success Indicators**

✅ **Homepage loads** with channel list  
✅ **M3U8 URLs generate** without errors  
✅ **VLC detects** stream format properly  
✅ **Network access** works from other devices  
✅ **Search functionality** filters channels  

### 🚀 **Additional Features Added**

#### **Search Functionality**
- **Live search** as you type
- **Filter by** name, genre, language
- **URL persistence** for search results

#### **Environment Variables**
- **SERVER_HOST** - Set your server IP
- **SERVER_PORT** - Set your desired port
- **Automatic detection** fallback

#### **Enhanced Interface**
- **Real-time cookie status**
- **Network configuration display**
- **Troubleshooting links**
- **Mobile-responsive design**

The system now properly handles VLC streaming requests and provides flexible network configuration for VM deployments! 🎬✨