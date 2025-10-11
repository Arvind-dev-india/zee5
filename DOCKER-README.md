# ZEE5 Streaming - Docker Setup

This guide helps you run the ZEE5 streaming script using Docker, without needing to install PHP, Apache, or any other dependencies on your system.

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose

### Installation & Usage

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd zee5
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - **Homepage**: `http://localhost:5052/` (Lists all channels with cookie status)
   - **M3U Playlist**: `http://localhost:5052/playlist.php` (For IPTV players)
   - **Individual Stream**: `http://localhost:5052/stream.php?id=CHANNEL_ID`

### 🛑 Stop the Application
```bash
docker-compose down
```

### 🎬 New Enhanced Features

#### 🏠 **Beautiful Homepage** (`http://localhost:5052/`)
- **Channel Grid**: Visual display of all available channels
- **Cookie Status**: Shows authentication expiry time
- **One-Click Streaming**: Direct stream links for each channel
- **M3U8 URLs**: Easy copy-paste URLs for VLC and other players
- **IPTV Playlist**: Direct access to M3U playlist
- **Responsive Design**: Works on mobile, tablet, and desktop

#### 📱 **Easy Channel Access**
- Click **"Stream Now"** to open channel directly
- Click **"Get M3U8"** to get the streaming URL for VLC
- Copy URLs with one click
- Open directly in VLC player

#### ⏰ **Cookie Management**
- Real-time cookie expiry status
- Automatic renewal when expired
- Visual indicators for authentication state

### 🔧 Advanced Usage

#### Custom Port
The service now runs on port **5052** by default. To change it, modify `docker-compose.yml`:
```yaml
ports:
  - "9090:80"  # Change 5052 to your preferred port
```

#### Rebuild After Changes
If you modify the PHP files:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### View Logs
```bash
docker-compose logs -f zee5-app
```

#### Access Container Shell
```bash
docker-compose exec zee5-app bash
```

## 📁 Project Structure
```
zee5/
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker image configuration
├── index.php           # Enhanced homepage with channel list
├── stream.php          # Individual channel streaming
├── playlist.php        # M3U playlist generator
├── _functions.php      # Helper functions
├── data.json          # Channel data
└── tmp/               # Cache directory (auto-created)
```

## 🌐 Using with IPTV Players

After starting the Docker container, use these URLs in your IPTV player:

- **VLC**: `http://localhost:5052/playlist.php`
- **Tivimate**: `http://localhost:5052/playlist.php`
- **OTT Navigator**: `http://localhost:5052/playlist.php`

### 📱 Individual Channel URLs
For individual channels in VLC or other players:
- Format: `http://localhost:5052/stream.php?id=CHANNEL_ID`
- Example: `http://localhost:5052/stream.php?id=0-9-zeetamil`

## 🔧 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs zee5-app

# Rebuild from scratch
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

### Permission Issues
```bash
# Fix permissions on tmp directory
sudo chmod 777 tmp/
```

### Port Already in Use
If port 5052 is already in use, change it in `docker-compose.yml`:
```yaml
ports:
  - "5053:80"  # Use port 5053 instead
```

## ⚠️ Important Notes

- This setup is for **educational purposes only**
- The container runs with proper security contexts
- Cache files are stored in the `tmp/` directory
- The application automatically handles token extraction and caching
- Cookie expiry is displayed in real-time on the homepage

## 🐳 Docker Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services  
docker-compose down

# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up -d --build

# Remove everything including volumes
docker-compose down -v
```

## 🌍 Access from Other Devices

To access from other devices on your network, replace `localhost` with your computer's IP address:
- Find your IP: `ip addr show` (Linux) or `ipconfig` (Windows)
- Use: `http://YOUR_IP_ADDRESS:5052/`

Example: `http://192.168.1.100:5052/`

### 📺 For IPTV Players on Network Devices
Use: `http://YOUR_IP_ADDRESS:5052/playlist.php` in your IPTV app on other devices.