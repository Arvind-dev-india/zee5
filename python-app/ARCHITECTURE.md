# ZEE5 Streaming Service - Architecture Documentation

## 📐 System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │    Web     │  │    VLC     │  │  Tivimate  │  │   Kodi    │ │
│  │  Browser   │  │   Player   │  │   Player   │  │  Player   │ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Application                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer                              │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────────────────┐│  │
│  │  │  Routes   │  │  Stream   │  │      Playlist         ││  │
│  │  │  (Admin)  │  │  Endpoint │  │   Generation (M3U)    ││  │
│  │  └───────────┘  └───────────┘  └───────────────────────┘│  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                            │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │                  Service Layer                            │  │
│  │  ┌────────────────┐  ┌────────────────┐                  │  │
│  │  │Channel Service │  │ Stream Service │                  │  │
│  │  └────────────────┘  └────────────────┘                  │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                            │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │                   Core Layer                              │  │
│  │  ┌──────────────────────────────────────────────────────┐│  │
│  │  │           Cookie Manager (Pool)                      ││  │
│  │  │  • Cookie pool (3-5 cookies)                        ││  │
│  │  │  • Auto-refresh background task                      ││  │
│  │  │  • Rotation on failure                               ││  │
│  │  │  • Expiry tracking                                   ││  │
│  │  └──────────────────────────────────────────────────────┘│  │
│  │                                                            │  │
│  │  ┌──────────────────┐  ┌──────────────────────────────┐ │  │
│  │  │ Playwright       │  │  Token Generator             │ │  │
│  │  │ Service          │  │  • JWT tokens                │ │  │
│  │  │ • Browser auto   │  │  • Guest tokens              │ │  │
│  │  │ • Token extract  │  │  • API headers               │ │  │
│  │  └──────────────────┘  └──────────────────────────────┘ │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                            │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │                  Cache Layer                              │  │
│  │  ┌────────────┐                  ┌────────────────────┐  │  │
│  │  │   Redis    │ ◄──fallback───► │   File System      │  │  │
│  │  │  (Primary) │                  │   (Backup)         │  │  │
│  │  └────────────┘                  └────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │         ZEE5 Platform             │
          │  • API endpoints                  │
          │  • M3U8 streams                   │
          │  • Authentication                 │
          └───────────────────────────────────┘
```

---

## 🔧 Component Details

### 1. Cookie Manager

**Purpose**: Manages authentication cookies for ZEE5 API access

**Key Features**:
- Cookie pool with configurable size (default: 3)
- Automatic rotation when cookie fails
- Background refresh task (every 10 hours)
- Expiry tracking and preemptive refresh
- Thread-safe operations with asyncio locks

**Flow**:
```
1. Initialize pool → Generate N cookies
2. Background task → Check expiry every 5 minutes
3. On request → Return best cookie (most remaining time)
4. On failure → Mark invalid, rotate to next cookie
5. On low remaining → Trigger refresh
6. Save to cache → Redis (primary) + File (backup)
```

**Code Location**: `app/core/cookie_manager.py`

---

### 2. Playwright Service

**Purpose**: Browser automation for extracting platform tokens and cookies

**Process**:
```
1. Launch headless Chromium browser
2. Navigate to ZEE5 page
3. Extract platform token from page content
4. Fetch M3U8 URL using token
5. Extract hdntl cookie from M3U8 response
6. Return cookie for caching
```

**Optimization**:
- Single browser instance (reused)
- Connection pooling
- Timeout configuration
- Mutex locks for concurrent requests

**Code Location**: `app/core/playwright_service.py`

---

### 3. Token Generator

**Purpose**: Generate authentication tokens for ZEE5 API

**Token Types**:

1. **DD Token (Device Details)**
   - JWT format (unsigned, alg=none)
   - Contains device capabilities
   - Player specifications
   - Security capabilities

2. **Guest Token**
   - UUID v4 format
   - Random hex string
   - Used as device ID

3. **Platform Token**
   - Extracted from ZEE5 website
   - Changes periodically
   - Required for API authentication

**Code Location**: `app/core/token_generator.py`

---

### 4. Cache Layer

**Purpose**: High-performance caching with redundancy

**Strategy**:
```
Priority:
1. Redis (if available) - Fast, distributed
2. File system - Reliable, always available
3. On-demand generation - Fallback

TTL: 12 hours (43000 seconds)
```

**Operations**:
- `get(key)` - Try Redis → File → None
- `set(key, value, ttl)` - Write to both
- `delete(key)` - Delete from both
- `clear_expired()` - Cleanup task (hourly)

**Code Location**: `app/core/cache.py`

---

### 5. Stream Service

**Purpose**: Generate stream URLs for channels

**Process**:
```
1. Validate channel ID
2. Get cookie from pool
3. Append cookie to base M3U8 URL
4. Return stream URL (with cookie parameter)
```

**URL Format**:
```
https://z5ak-cmaflive.zee5.com/cmaf/live/2105531/ZeeTVHDMSLELE/index.m3u8?hdntl=<cookie_value>
```

**Code Location**: `app/services/stream_service.py`

---

### 6. Channel Service

**Purpose**: Manage channel data and metadata

**Features**:
- Load channels from JSON
- Search and filter
- Channel lookup by ID
- Genre/language/country filtering

**Code Location**: `app/services/channel_service.py`

---

## 🔄 Request Flow

### Stream Request Flow

```
1. Client requests /stream?id=0-9-zeetv
   │
   ▼
2. Stream endpoint validates channel ID
   │
   ▼
3. Stream service retrieves channel data
   │
   ▼
4. Cookie manager provides valid cookie
   │
   ├─→ Cache hit → Return cached cookie
   │
   └─→ Cache miss → Generate new cookie
       │
       ├─→ Playwright extracts platform token
       │
       ├─→ Token generator creates tokens
       │
       ├─→ Fetch M3U8 URL from ZEE5 API
       │
       └─→ Extract hdntl cookie from M3U8
   │
   ▼
5. Build final stream URL (base + cookie)
   │
   ▼
6. Return 302 redirect to stream URL
```

### M3U Playlist Flow

```
1. Client requests /playlist.m3u
   │
   ▼
2. Generate random user agent
   │
   ▼
3. Load all channels from service
   │
   ▼
4. For each channel:
   ├─→ Add EXTINF metadata
   ├─→ Add KODIPROP headers
   ├─→ Add EXTVLCOPT options
   └─→ Add stream endpoint URL
   │
   ▼
5. Return M3U8 formatted playlist
```

---

## 🔐 Authentication Flow

### ZEE5 API Authentication

```
Step 1: Get Platform Token
┌─────────────────────────────────────┐
│ Playwright visits ZEE5 website      │
│ Extracts: gwapiPlatformToken        │
│ Method: Regex from page content     │
└─────────────────────────────────────┘
              │
              ▼
Step 2: Generate Tokens
┌─────────────────────────────────────┐
│ Guest Token: UUID v4 format         │
│ DD Token: JWT (device details)      │
└─────────────────────────────────────┘
              │
              ▼
Step 3: API Request
┌─────────────────────────────────────┐
│ POST to singlePlayback/getDetails   │
│ Headers: platform token, user-agent │
│ Body: guest token, DD token         │
└─────────────────────────────────────┘
              │
              ▼
Step 4: Get M3U8 URL
┌─────────────────────────────────────┐
│ Response: keyOsDetails.video_token  │
│ Contains: Base M3U8 URL             │
└─────────────────────────────────────┘
              │
              ▼
Step 5: Extract Cookie
┌─────────────────────────────────────┐
│ Fetch M3U8 URL                      │
│ Extract: hdntl parameter            │
│ Format: hdntl=<encrypted_value>     │
└─────────────────────────────────────┘
```

---

## ⚡ Background Tasks

### 1. Cookie Refresh Task

**Interval**: Every 5 minutes (check)
**Trigger Conditions**:
- No valid cookies available
- Next scheduled refresh time reached
- All cookies expiring soon (<1 hour)

**Process**:
```python
async def cookie_refresh_task():
    while True:
        await asyncio.sleep(300)  # 5 minutes

        if await cookie_manager.should_refresh():
            await cookie_manager.refresh_pool()
```

### 2. Cache Cleanup Task

**Interval**: Every hour
**Purpose**: Remove expired file cache entries

**Process**:
```python
async def cache_cleanup_task():
    while True:
        await asyncio.sleep(3600)  # 1 hour
        await cache.clear_expired()
```

---

## 📊 Data Models

### Cookie Model
```python
class Cookie(BaseModel):
    value: str                  # hdntl=...
    created_at: datetime
    expires_at: datetime
    is_valid: bool
    user_agent: str
    failure_count: int
```

### Channel Model
```python
class Channel(BaseModel):
    id: str                     # 0-9-zeetv
    name: str                   # Zee TV HD
    country: str                # IN
    language: str               # hi
    genre: str                  # Entertainment
    url: HttpUrl                # M3U8 base URL
    logo: HttpUrl
    chno: str
```

### Stream Response Model
```python
class StreamResponse(BaseModel):
    success: bool
    channel: Optional[Channel]
    stream_url: Optional[str]   # Full URL with cookie
    cached: bool
    expires_in: int
    error: Optional[str]
```

---

## 🛡️ Error Handling

### Error Hierarchy

```
1. API Level
   ├─→ HTTPException (4xx, 5xx)
   └─→ ErrorResponse model

2. Service Level
   ├─→ Try/catch with logging
   └─→ Return error in response model

3. Core Level
   ├─→ Retry logic (cookie generation)
   ├─→ Fallback mechanisms (cache)
   └─→ Graceful degradation
```

### Retry Strategy

**Cookie Generation**:
- Max retries: 3
- Backoff: Exponential (2s, 4s, 8s)
- Failure handling: Mark cookie invalid, rotate

**API Requests**:
- Timeout: 30 seconds
- Retry on network errors: Yes
- Retry on 5xx: Yes (max 2)

---

## 🔍 Monitoring & Observability

### Health Check Endpoint

```
GET /health

Returns:
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "cache": "healthy",
    "channels": "healthy",
    "cookie_manager": "healthy"
  },
  "cookie_pool": {
    "valid_cookies": 3,
    "total_cookies": 3,
    ...
  }
}
```

### Debug Endpoints

- `/cookie/status` - Detailed cookie pool status
- `/debug` - Debug page with testing tools
- `/channels/stats` - Channel statistics
- `/debug/info` - Application configuration

### Logging

**Levels**:
- DEBUG: Detailed flow information
- INFO: Service lifecycle events
- WARNING: Degraded performance
- ERROR: Operation failures

**Format**:
```
2025-01-15 10:30:45 - zee5.cookie_manager - INFO - Generated cookie (expires in 43000s)
```

---

## 🚀 Performance Optimizations

### 1. Connection Pooling
- HTTP client: httpx.AsyncClient
- Persistent connections
- Keep-alive enabled

### 2. Async Operations
- All I/O operations are async
- Non-blocking cookie generation
- Concurrent request handling

### 3. Caching Strategy
- Redis for speed (sub-ms latency)
- File cache for reliability
- 12-hour TTL reduces API calls

### 4. Cookie Pool
- Multiple cookies prevent bottleneck
- Auto-rotation distributes load
- Preemptive refresh avoids downtime

---

## 🔧 Configuration

### Environment Variables

```bash
# Core
APP_NAME=ZEE5 Streaming Service
APP_VERSION=2.0.0
DEBUG=false

# Server
HOST=0.0.0.0
PORT=5052
SERVER_URL=http://localhost:5052

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
USE_REDIS=true

# Cookie Pool
COOKIE_POOL_SIZE=3
COOKIE_REFRESH_INTERVAL=36000
COOKIE_MIN_REMAINING=3600

# Playwright
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=60000

# Logging
LOG_LEVEL=INFO
LOG_JSON=false
```

---

## 📈 Scalability Considerations

### Horizontal Scaling

**Current**: Single instance with cookie pool
**Future**: Multi-instance with shared Redis

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│Instance 1│  │Instance 2│  │Instance 3│
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │             │             │
      └─────────────┼─────────────┘
                    │
              ┌─────▼─────┐
              │   Redis   │
              │  (Shared  │
              │   Cache)  │
              └───────────┘
```

**Required Changes**:
- Distributed locking for cookie generation
- Shared cookie pool in Redis
- Load balancer for request distribution

### Vertical Scaling

- Increase cookie pool size
- Add more Playwright instances
- Optimize cache size

---

## 🔒 Security Considerations

1. **No User Authentication**
   - Service is publicly accessible
   - Consider adding API keys for production

2. **Rate Limiting**
   - Currently not implemented
   - Add per-IP rate limits to prevent abuse

3. **Cookie Security**
   - Cookies stored in cache (file/Redis)
   - No sensitive data exposure
   - Auto-expiry prevents stale cookies

4. **CORS**
   - Currently allows all origins (*)
   - Restrict in production

---

## 📝 Future Enhancements

1. **Multi-region Support**
   - Proxy rotation for geo-restrictions
   - Regional cookie pools

2. **Analytics**
   - Track popular channels
   - Usage statistics
   - Performance metrics

3. **EPG Integration**
   - Electronic Program Guide
   - Schedule information

4. **User Management**
   - Optional authentication
   - User preferences
   - Favorites

5. **CDN Integration**
   - Serve static files from CDN
   - Reduce server load

---

## 🤝 Contributing

See main [README.md](README.md) for contribution guidelines.

---

**Last Updated**: 2025-01-15
**Version**: 2.0.0
