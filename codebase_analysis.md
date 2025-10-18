# ZEE5 Streaming Service - Codebase Analysis

## Executive Summary

This is a PHP-based IPTV streaming service that proxies ZEE5 live TV channels. The system handles authentication through cookie-based token management and serves streams to IPTV players via M3U playlists. The current architecture relies on client-side user agent handling and server-side authentication token extraction and caching.

---

## 1. CURRENT COOKIE GENERATION APPROACH

### 1.1 Overview
Cookies are generated **server-side** using PHP through a multi-step authentication process:

1. **Guest Token Generation** - Random UUID-like string
2. **Platform Token Extraction** - Extracted from ZEE5 website by scraping
3. **DD Token Creation** - JWT-like token with device capabilities
4. **Final Authentication** - hdntl token extracted from M3U8 master playlist

### 1.2 Cookie Generation Flow

**File:** `/home/arvind/projects/zee5/_functions.php`

```php
function generateCookieZee5($userAgent) {
    // Step 1: Generate guest token (random UUID)
    $guestToken = generateGuestToken();
    
    // Step 2: Extract platform token from ZEE5 website
    $platformToken = fetchPlatformToken();
    
    // Step 3: Create DD token (device capabilities JWT)
    $ddToken = generateDDToken();
    
    // Step 4: Make API request with tokens
    // POST to: https://spapi.zee5.com/singlePlayback/getDetails/secure
    
    // Step 5: Extract final hdntl token from M3U8 response
    // Pattern: hdntl=([^,\s]+)
    
    return ['cookie' => "hdntl=..."];
}
```

### 1.3 Cookie Caching Strategy

**File:** `/home/arvind/projects/zee5/stream.php` & `get-stream-url.php`

```php
function getCookieZee5($userAgent) {
    $UAhash = md5($userAgent);
    $cacheFile = "tmp/cookie_z5_$UAhash.tmp";
    
    $cacheExpiry = 43000; // 12 hours
    
    // Check if cached and still valid
    if (file_exists($cacheFile) && (time() - filemtime($cacheFile) < $cacheExpiry)) {
        return file_get_contents($cacheFile);
    }
    
    // Generate new cookie if expired or doesn't exist
    $data = generateCookieZee5($userAgent);
    @file_put_contents($cacheFile, $data['cookie']);
    return $data['cookie'];
}
```

**Cache Location:** `/home/arvind/projects/zee5/tmp/` (file-based with MD5-hashed user agent names)

---

## 2. PHP FILES INVOLVED

### File Structure
```
/home/arvind/projects/zee5/
├── index.php                    # Web UI - Channel browser
├── playlist.php                 # M3U playlist generator
├── stream.php                   # Stream redirect endpoint
├── get-stream-url.php           # JSON API for stream URLs
├── _functions.php               # Core authentication functions
├── get-server-info.php          # Server configuration helper
├── debug-stream.php             # Debugging utility
└── data.json                    # Channel database
```

### 2.1 Index.php - Web Interface
**Purpose:** Channel browser with cookie status dashboard

**Key Features:**
- Cookie expiry calculation and display
- Channel search and filtering
- M3U playlist link generation
- Real-time status indicator
- Direct streaming buttons

**Authentication Interaction:**
```php
function getCookieExpiry($userAgent) {
    $UAhash = md5($userAgent);
    $cacheFile = "tmp/cookie_z5_$UAhash.tmp";
    
    if (file_exists($cacheFile)) {
        $fileTime = filemtime($cacheFile);
        $expiryTime = $fileTime + 43000; // 12 hours
        $remaining = $expiryTime - time();
        return [
            'exists' => true,
            'expires_at' => date('Y-m-d H:i:s', $expiryTime),
            'remaining_hours' => round($remaining / 3600, 1),
            'is_expired' => $remaining <= 0
        ];
    }
    return ['exists' => false];
}
```

### 2.2 Playlist.php - IPTV Playlist Generator
**Purpose:** Generate M3U playlist for IPTV players

**Format:** #EXTM3U with EXTINF entries pointing to stream.php

**Key Features:**
- Randomized user agent per playlist generation
- Kodiprop directives for Kodi players
- VLC HTTP header options
- Channel metadata (ID, logo, language, etc.)

**Example Output:**
```
#EXTM3U
#EXTINF:-1 tvg-id="0-9-zeetamil" tvg-name="Zee Tamil HD" tvg-logo="..." group-title="Entertainment",Zee Tamil HD [TA]
#EXTVLCOPT:http-user-agent=Mozilla/5.0...
http://localhost:5052/stream.php?id=0-9-zeetamil
```

### 2.3 Stream.php - Stream Redirect Handler
**Purpose:** Authenticate user agent, generate/cache cookie, redirect to stream

**Flow:**
1. Extract channel ID from GET parameter
2. Get user agent from request
3. Retrieve/generate authentication cookie
4. Append cookie as query parameter to streaming URL
5. Redirect or return URL based on client type

**Output:**
- For media players: Plain text URL
- For browsers: HTTP 302 redirect
- On error: HTTP error code with message

### 2.4 Get-stream-url.php - JSON API
**Purpose:** AJAX endpoint for getting stream URLs

**Returns JSON:**
```json
{
    "success": true,
    "channel": {
        "id": "0-9-zeetamil",
        "name": "Zee Tamil HD",
        "genre": "Entertainment",
        "language": "ta"
    },
    "stream_url": "https://z5ak-cmaflive.zee5.com/...?hdntl=...",
    "cached": true,
    "expires_in": 43000
}
```

### 2.5 _functions.php - Core Authentication Functions
**Purpose:** All authentication logic and token generation

**Functions:**
1. `generateGuestToken()` - Random UUID-like string (36 chars)
2. `fetchPlatformToken()` - Scrapes platform token from zee5.com
3. `generateDDToken()` - Creates JWT-like device capabilities token
4. `fetchM3U8url()` - Calls ZEE5 API to get M3U8 URL
5. `generateCookieZee5($userAgent)` - Main cookie generation orchestrator
6. `base64UrlEncode()` - JWT encoding helper

**Critical API Endpoint:**
```
POST https://spapi.zee5.com/singlePlayback/getDetails/secure
Parameters:
  - device_id: Guest token
  - platform_name: desktop_web
  - channel_id: ZEE5 channel ID
  - user_type: guest
Headers:
  - x-access-token: Platform token
  - X-Z5-Guest-Token: Guest token
  - x-dd-token: DD token
```

### 2.6 Get-server-info.php - Server Configuration
**Purpose:** Auto-detect server URL and configuration

**Logic:**
- Reads from environment variables (SERVER_HOST, SERVER_PORT)
- Falls back to request headers (HTTP_HOST)
- Detects protocol (HTTP/HTTPS)
- Handles X-Forwarded headers for reverse proxies
- Returns base URL for client redirection

### 2.7 Debug-stream.php - Debugging Utility
**Purpose:** Detailed troubleshooting and verification

**Checks:**
- Directory permissions (tmp/ writable)
- Cookie cache status
- Channel data validation
- Cookie generation with timing
- URL accessibility test
- HTTP response codes

---

## 3. AUTHENTICATION & SESSION MANAGEMENT

### 3.1 Authentication Mechanism
**Type:** Stateless, User-Agent Based

**Key Concepts:**
- No user accounts or login
- Authentication based on unique device/user agent
- Cookies cached per user agent
- Each user agent can have its own cached cookie

**Session Lifecycle:**
```
User Agent Request
    ↓
Check MD5(User Agent) cache file
    ↓
Cache valid & fresh?
    ├─ YES → Use cached cookie (12 hours max)
    └─ NO → Generate new cookie
         ↓
    Extract tokens from ZEE5
         ↓
    Call API with tokens
         ↓
    Extract hdntl token from response
         ↓
    Cache for 12 hours
    ↓
Append to streaming URL
    ↓
Stream to client
```

### 3.2 Session Persistence
- **Duration:** 12 hours (43000 seconds)
- **Storage:** File system (tmp/ directory)
- **Uniqueness:** Keyed by MD5 hash of User-Agent
- **Invalidation:** File deletion or timeout
- **Refresh:** Automatic on expiry

### 3.3 No Traditional Session Management
- **No PHP sessions:** No $_SESSION used
- **No database:** Pure file-based caching
- **No tokens in headers:** Tokens appended to URL as query parameter
- **Stateless:** Each request can verify itself independently

---

## 4. WHY THIS DOESN'T WORK FOR IPTV CLIENTS

### 4.1 The Core Problem: Client-Side Dependency

**Current Implementation:**
1. **Playlist.php** generates M3U file with stream.php URLs
2. IPTV player receives M3U and creates playback requests
3. **stream.php** receives request from IPTV player
4. stream.php examines player's User-Agent header
5. Generates/retrieves cookie based on THAT user agent
6. Returns URL with cookie appended

**The Problem:**
```
Browser                          IPTV Player (VLC, Tivimate, etc)
   │                                    │
   ├─ Request playlist.php              │
   │  (User-Agent: Chrome/Firefox)      │
   │                                    ├─ Receives M3U
   │                                    │
   │                                    ├─ Tries to play stream
   │                                    │  (User-Agent: VLC/Tivimate/etc)
   │                                    │
   │                                    ├─ Requests stream.php?id=...
   │                                    │  User-Agent: VLC 3.0
   │                                    │
   │                                    ├─ stream.php generates cookie for VLC user agent
   │                                    │  Creates cache: cookie_z5_[VLC_HASH].tmp
   │                                    │
   │                                    └─ Returns URL with VLC-specific cookie
```

**Specific Issues:**

1. **IPTV Players Don't Execute JavaScript**
   - Current code includes JavaScript in index.php for UI interactions
   - IPTV players (VLC, Tivimate, OTT Navigator) don't run JS
   - They only parse M3U playlists and make HTTP requests
   - Cookies generated via JavaScript won't work

2. **User Agent Mismatches**
   - Browser generates playlist with User-Agent: Chrome
   - VLC player requests with User-Agent: VLC
   - Cache lookup misses: `cookie_z5_[CHROME_HASH].tmp` vs `cookie_z5_[VLC_HASH].tmp`
   - Same user now needs TWO separate cached cookies

3. **Each Device Gets Different Cookies**
   - Phone (Android user agent) → Different cookie than Desktop (Chrome)
   - Tablet (Safari user agent) → Different cookie than Phone
   - Results in cache explosion and token generation spam

4. **No Client-Side Cookie Management**
   - HTTP cookies are NOT sent with M3U requests
   - IPTV players don't maintain persistent cookies
   - Can't rely on Set-Cookie headers
   - Authentication must be in URL (query parameter)

5. **Timeouts During Generation**
   - generateCookieZee5() makes 2-3 cURL requests
   - Takes 2-5 seconds per new cookie generation
   - IPTV players timeout waiting for stream to start
   - No retry mechanism in most IPTV players

---

## 5. CURRENT ARCHITECTURE FLOW

### 5.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    External (ZEE5 Live)                     │
│    https://z5ak-cmaflive.zee5.com/cmaf/live/...m3u8         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Authentication Layer (_functions.php)           │
│  - Generate Guest Token                                      │
│  - Fetch Platform Token                                      │
│  - Generate DD Token                                         │
│  - Call ZEE5 API (spapi.zee5.com)                           │
│  - Extract hdntl Token                                       │
│  - Cache for 12 hours                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   PHP Application Layer                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐         │
│  │ index.php   │  │ playlist.php  │  │ stream.php  │         │
│  │ Web UI      │  │ M3U Generator │  │ Redirector  │         │
│  └─────────────┘  └──────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Caching Layer                             │
│    tmp/cookie_z5_[USER_AGENT_MD5].tmp (12 hour TTL)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                       Clients                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Browser  │  │   VLC    │  │ Tivimate │  │   OTT    │    │
│  │(Web UI)  │  │  (Local) │  │  (App)   │  │Navigator │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Request Flow for Web Browser

```
1. User visits http://localhost:5052/
   ↓
2. index.php:
   - Load data.json (channel list)
   - Get user's User-Agent header
   - MD5 hash it
   - Check tmp/cookie_z5_[HASH].tmp for status
   - Display cookie expiry on homepage
   ↓
3. User clicks "Stream Now"
   ↓
4. stream.php?id=0-9-zeetamil:
   - Extract channel ID
   - Get User-Agent (Chrome in this case)
   - Call getCookieZee5(userAgent)
   - Check cache (tmp/cookie_z5_[CHROME_HASH].tmp)
   - If not found or expired:
     - Call generateCookieZee5(userAgent)
     - This calls multiple ZEE5 APIs
     - Extracts final hdntl token
     - Caches it
   - Append cookie to base stream URL
   - Redirect to https://z5ak-cmaflive.zee5.com/...?hdntl=abc123
   ↓
5. Browser receives stream from ZEE5
```

### 5.3 Request Flow for IPTV Player

```
1. User adds playlist to VLC/Tivimate
   URL: http://192.168.1.10:5052/playlist.php
   ↓
2. IPTV Player requests playlist.php:
   User-Agent: VLC/3.0.0 or Tivimate/2.x
   ↓
3. playlist.php generates M3U:
   - Reads data.json
   - Generates randomized User-Agent (Chrome-like)
   - For each channel, creates entry:
     #EXTINF:-1 tvg-id="..." tvg-name="Zee Tamil HD" ...
     http://192.168.1.10:5052/stream.php?id=0-9-zeetamil
   - Returns M3U with 90+ channel entries
   ↓
4. IPTV player parses M3U and starts playback
   For each channel:
   ├─ Request: http://192.168.1.10:5052/stream.php?id=0-9-zeetamil
   │  User-Agent: VLC/3.0.0 (NOT Chrome!)
   ↓
5. stream.php processes request:
   - Get channel URL from data.json
   - Get User-Agent: VLC/3.0.0
   - Hash it: MD5(VLC/3.0.0) = 12345...
   - Check tmp/cookie_z5_12345....tmp
   - NO MATCH! (Chrome cookie was from Browser request)
   - Must generate new cookie for VLC
   - Takes 2-5 seconds (multiple API calls)
   ↓
6. IPTV player timeout:
   - Waits 10 seconds max for stream redirect
   - stream.php still generating token
   - Connection times out
   - "Stream unavailable" error
   ↓
7. If stream.php completes in time:
   - Returns: https://z5ak-cmaflive.zee5.com/...?hdntl=xyz789
   - IPTV player streams successfully
   - Cookie cached for VLC user agent
   - Next request uses cache (fast)
```

### 5.4 Data Flow Diagram

```
Data.json (Channel Database)
    │
    ├─→ index.php (Display channels, show cookie status)
    │   │
    │   └─→ getCookieExpiry() (Read tmp/ cache)
    │
    ├─→ playlist.php (Generate M3U)
    │   │
    │   └─→ For each channel: stream.php?id=...
    │
    └─→ stream.php (Stream redirect)
        │
        ├─→ getCookieZee5(userAgent) {
        │   │
        │   ├─→ Cache Hit? Return cached cookie
        │   │
        │   └─→ Cache Miss? Call generateCookieZee5()
        │       │
        │       ├─→ generateGuestToken() [Random]
        │       ├─→ fetchPlatformToken() [Scrape ZEE5]
        │       ├─→ generateDDToken() [JWT]
        │       ├─→ fetchM3U8url() [API call]
        │       └─→ generateCookieZee5() [Extract from M3U8]
        │
        └─→ Return: stream_url + auth_cookie
```

---

## 6. KEY FILES SUMMARY

| File | Purpose | Size | Dependency |
|------|---------|------|------------|
| **_functions.php** | Core auth logic | ~5.5 KB | External ZEE5 APIs (requires curl) |
| **index.php** | Web UI dashboard | ~20 KB | _functions.php, data.json |
| **playlist.php** | M3U generator | ~3.8 KB | data.json, get-server-info.php |
| **stream.php** | Stream redirector | ~3 KB | _functions.php |
| **get-stream-url.php** | JSON API | ~3 KB | _functions.php |
| **get-server-info.php** | Config helper | ~1.3 KB | - |
| **debug-stream.php** | Debugging | ~5.9 KB | _functions.php |
| **data.json** | Channel database | ~47 KB | - |

---

## 7. AUTHENTICATION LAYERS

### 7.1 Layer 1: Token Generation (On-Demand)
- Triggered when cache miss
- Requires live internet + Indian IP
- Makes multiple external API calls
- Time-intensive (2-5 seconds)

### 7.2 Layer 2: URL-Based Auth
- Cookies appended as query parameter: `?hdntl=...`
- Not HTTP Set-Cookie
- Must be in M3U URLs for IPTV players

### 7.3 Layer 3: User-Agent Detection
- Each unique UA gets separate cache
- Browser UA differs from IPTV player UA
- Can cause cache misses

### 7.4 Layer 4: ZEE5 Server-Side Validation
- External CDN validates hdntl token
- Geo-IP checks (India only)
- Token expiry validation

---

## 8. CRITICAL FINDINGS

### Problems with Current Implementation:

1. **Cache Fragmentation**
   - One cache file per user agent
   - Browser + VLC = 2 cache files
   - Multiple devices = exponential cache growth
   - Wastes storage and causes repeated auth calls

2. **Timing Issues**
   - Auth generation takes 2-5 seconds
   - IPTV players timeout in 10 seconds
   - On busy network, first channel always fails
   - Subsequent channels work (from cache)

3. **User Agent Volatility**
   - User agents change frequently
   - Browser updates change UA string
   - IPTV app versions change UA
   - Cache hits become unreliable

4. **No User Identification**
   - Can't track per-user limits
   - Can't rate limit abusive clients
   - Can't revoke authentication
   - All clients share same pool

5. **IP Geo-blocking at ZEE5**
   - All auth requests from server IP
   - Server must be in India or using Indian IP
   - External proxies can't be used for auth
   - No VPN bypass in current code

---

## Conclusion

The current architecture is a **server-side caching proxy** that:
- Generates authentication tokens server-side
- Caches them by user agent
- Appends auth to URLs for IPTV players
- Works best for browser clients
- Struggles with diverse IPTV player user agents

The main limitation is the **user agent-based caching strategy**, which doesn't scale well for heterogeneous IPTV environments where different players and devices have different user agents.
