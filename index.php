<?php
//=============================================================================//
// FOR EDUCATION PURPOSE ONLY. Don't Sell this Script, This is 100% Free.
// Join Community https://t.me/ygxworld, https://t.me/ygx_chat
//=============================================================================//
include_once '_functions.php';
include_once 'get-server-info.php';

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
            'remaining_seconds' => $remaining,
            'is_expired' => $remaining <= 0
        ];
    }
    return ['exists' => false];
}

// Load channel data
$file = 'data.json';
$json_data = file_get_contents($file);
$data = json_decode($json_data, true);
$userAgent = $_SERVER['HTTP_USER_AGENT'] ?? "Mozilla/5.0";
$cookieInfo = getCookieExpiry($userAgent);

// Get server info
$serverInfo = getServerInfo();
$baseUrl = $serverInfo['base_url'];

// Handle search
$searchQuery = $_GET['search'] ?? '';
$filteredChannels = $data['data'];

if ($searchQuery) {
    $filteredChannels = array_filter($data['data'], function($channel) use ($searchQuery) {
        return stripos($channel['name'], $searchQuery) !== false ||
               stripos($channel['genre'], $searchQuery) !== false ||
               stripos($channel['language'], $searchQuery) !== false ||
               stripos($channel['id'], $searchQuery) !== false;
    });
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZEE5 Streaming - Channel List</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .server-info {
            background: #e3f2fd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
            border-left: 5px solid #2196f3;
        }
        
        .search-container {
            margin-bottom: 30px;
            text-align: center;
        }
        
        .search-box {
            width: 100%;
            max-width: 500px;
            padding: 15px 20px;
            font-size: 1.1em;
            border: 2px solid #ddd;
            border-radius: 25px;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .search-box:focus {
            border-color: #007bff;
            box-shadow: 0 0 10px rgba(0, 123, 255, 0.3);
        }
        
        .search-results {
            margin-top: 10px;
            color: #666;
            font-size: 0.9em;
        }
        
        .cookie-status {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 5px solid #007bff;
        }
        
        .cookie-status.expired {
            border-left-color: #dc3545;
            background: #fff5f5;
        }
        
        .cookie-status h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .playlist-links {
            background: #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .playlist-links h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 25px;
            margin: 5px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
        }
        
        .btn-primary:hover {
            background: #0056b3;
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #1e7e34;
            transform: translateY(-2px);
        }
        
        .channels-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .channel-card {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
            border: 1px solid #e9ecef;
        }
        
        .channel-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }
        
        .channel-header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            text-align: center;
        }
        
        .channel-header h4 {
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        
        .channel-info {
            padding: 15px;
        }
        
        .channel-meta {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #666;
        }
        
        .channel-actions {
            text-align: center;
        }
        
        .btn-sm {
            padding: 8px 15px;
            font-size: 0.9em;
            margin: 2px;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
            color: #666;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            text-align: center;
            flex-wrap: wrap;
        }
        
        .stat-item {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            min-width: 150px;
            margin: 5px;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .channels-grid {
                grid-template-columns: 1fr;
            }
            .stats {
                flex-direction: column;
                gap: 15px;
            }
        }
        
        .copy-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 0.8em;
            margin-left: 10px;
        }
        
        .copy-btn:hover {
            background: #5a6268;
        }
        
        .url-display {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            word-break: break-all;
            font-size: 0.9em;
            border: 1px solid #e9ecef;
        }
        
        .no-results {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .no-results h3 {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 ZEE5 Streaming Server</h1>
            <p class="subtitle">All Channels • High Quality • Ready to Stream</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                <a href="/debug-stream.php" style="color: #007bff;">🔧 Debug Tools</a> | 
                <a href="/STREAMING-TROUBLESHOOTING.md" style="color: #007bff;">📖 Troubleshooting Guide</a>
            </p>
        </div>
        
        <div class="server-info">
            <h3>🌐 Server Configuration</h3>
            <p><strong>Base URL:</strong> <?php echo htmlspecialchars($baseUrl); ?></p>
            <p><strong>Network Access:</strong> Replace localhost with your server IP for network access</p>
        </div>
        
        <div class="search-container">
            <form method="GET" style="display: inline-block; width: 100%;">
                <input type="text" name="search" class="search-box" 
                       placeholder="🔍 Search channels by name, genre, or language..." 
                       value="<?php echo htmlspecialchars($searchQuery); ?>"
                       onkeyup="liveSearch(this.value)">
            </form>
            <div class="search-results" id="searchResults">
                <?php if ($searchQuery): ?>
                    Found <?php echo count($filteredChannels); ?> channel(s) matching "<?php echo htmlspecialchars($searchQuery); ?>"
                    <a href="/" style="margin-left: 10px; color: #007bff;">Clear Search</a>
                <?php else: ?>
                    Showing all <?php echo count($data['data']); ?> channels
                <?php endif; ?>
            </div>
        </div>
        
        <div class="cookie-status <?php echo $cookieInfo['exists'] && $cookieInfo['is_expired'] ? 'expired' : ''; ?>">
            <h3>🔐 Authentication Status</h3>
            <?php if ($cookieInfo['exists']): ?>
                <?php if ($cookieInfo['is_expired']): ?>
                    <p><strong>Status:</strong> ❌ Expired</p>
                    <p>Cookie expired. It will be renewed automatically on first channel access.</p>
                <?php else: ?>
                    <p><strong>Status:</strong> ✅ Active</p>
                    <p><strong>Expires:</strong> <?php echo $cookieInfo['expires_at']; ?></p>
                    <p><strong>Remaining:</strong> <?php echo $cookieInfo['remaining_hours']; ?> hours</p>
                <?php endif; ?>
            <?php else: ?>
                <p><strong>Status:</strong> 🆕 Not initialized</p>
                <p>Cookie will be generated automatically on first channel access.</p>
            <?php endif; ?>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number"><?php echo count($filteredChannels); ?></div>
                <div class="stat-label"><?php echo $searchQuery ? 'Filtered' : 'Total'; ?> Channels</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">HD</div>
                <div class="stat-label">Quality</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">24/7</div>
                <div class="stat-label">Available</div>
            </div>
        </div>
        
        <div class="playlist-links">
            <h3>📺 IPTV Playlist Links</h3>
            <a href="<?php echo $baseUrl; ?>/playlist.php" class="btn btn-primary" target="_blank">🔗 Open M3U Playlist</a>
            <button class="copy-btn" onclick="copyToClipboard('<?php echo $baseUrl; ?>/playlist.php')">📋 Copy URL</button>
            <div class="url-display" style="margin-top: 15px;">
                <?php echo $baseUrl; ?>/playlist.php
            </div>
            <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                Use this URL in VLC, Tivimate, OTT Navigator, or any IPTV player
            </p>
        </div>
        
        <h2 style="text-align: center; margin-bottom: 20px; color: #333;">
            <?php echo $searchQuery ? 'Search Results' : 'Available Channels'; ?>
        </h2>
        
        <?php if (empty($filteredChannels)): ?>
            <div class="no-results">
                <h3>😅 No channels found</h3>
                <p>Try a different search term or <a href="/">view all channels</a></p>
            </div>
        <?php else: ?>
            <div class="channels-grid">
                <?php foreach ($filteredChannels as $channel): ?>
                <div class="channel-card">
                    <div class="channel-header">
                        <h4><?php echo htmlspecialchars($channel['name']); ?></h4>
                        <small>CH <?php echo htmlspecialchars($channel['chno']); ?></small>
                    </div>
                    <div class="channel-info">
                        <div class="channel-meta">
                            <span><strong>Language:</strong> <?php echo strtoupper($channel['language']); ?></span>
                            <span><strong>Genre:</strong> <?php echo htmlspecialchars($channel['genre']); ?></span>
                        </div>
                        <div class="channel-actions">
                            <a href="<?php echo $baseUrl; ?>/stream.php?id=<?php echo urlencode($channel['id']); ?>" 
                               class="btn btn-primary btn-sm" target="_blank">
                                🎬 Stream Now
                            </a>
                            <button class="btn btn-success btn-sm" 
                                    onclick="showM3U8('<?php echo htmlspecialchars($channel['name']); ?>', '<?php echo htmlspecialchars($channel['id']); ?>')">
                                📱 Get M3U8
                            </button>
                        </div>
                    </div>
                </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
        
        <div class="footer">
            <p>🎯 For Educational Purposes Only • ❤️ Open Source • 🌟 Free Forever</p>
            <p style="margin-top: 10px;">
                <strong>Developers:</strong> <?php echo htmlspecialchars($data['developers']); ?> •
                <strong>Server:</strong> <?php echo htmlspecialchars($serverInfo['host'] . ':' . $serverInfo['port']); ?>
            </p>
        </div>
    </div>

    <!-- Modal for M3U8 URL Display -->
    <div id="m3u8Modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 15px; max-width: 90%; width: 500px;">
            <h3 style="margin-bottom: 20px; color: #333;" id="modalTitle">M3U8 Stream URL</h3>
            <div class="url-display" id="modalUrl" style="margin-bottom: 20px;"></div>
            <div style="text-align: center;">
                <button class="btn btn-primary" onclick="copyModalUrl()">📋 Copy URL</button>
                <button class="btn btn-success" onclick="openInVLC()">🎬 Open in VLC</button>
                <button class="btn" style="background: #6c757d; color: white;" onclick="closeModal()">❌ Close</button>
            </div>
            <p style="margin-top: 15px; color: #666; font-size: 0.9em; text-align: center;">
                📡 <strong>For VLC:</strong> Copy the URL above and paste in VLC → Media → Open Network Stream<br>
                🌍 <strong>Note:</strong> If streaming doesn't work, you may need a VPN with Indian IP address<br>
                🔧 <strong>Troubleshooting:</strong> Visit <a href="/debug-stream.php">Debug Page</a> | <a href="/STREAMING-TROUBLESHOOTING.md">Full Guide</a>
            </p>
        </div>
    </div>

    <script>
        let currentM3U8Url = '';
        let searchTimeout;
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                alert('URL copied to clipboard!');
            });
        }
        
        function showM3U8(channelName, channelId) {
            // Show loading
            document.getElementById('modalTitle').textContent = channelName + ' - Loading...';
            document.getElementById('modalUrl').textContent = 'Generating stream URL, please wait...';
            document.getElementById('m3u8Modal').style.display = 'block';
            
            // Get stream URL via AJAX
            fetch('/get-stream-url.php?id=' + encodeURIComponent(channelId))
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        currentM3U8Url = data.stream_url;
                        document.getElementById('modalTitle').textContent = channelName + ' - M3U8 URL';
                        document.getElementById('modalUrl').textContent = data.stream_url;
                        
                        // Add cache info
                        const cacheInfo = data.cached ? 
                            ' (Cached, expires in ' + Math.round(data.expires_in / 3600) + ' hours)' : 
                            ' (Newly generated)';
                        document.getElementById('modalTitle').textContent += cacheInfo;
                    } else {
                        document.getElementById('modalTitle').textContent = channelName + ' - Error';
                        document.getElementById('modalUrl').textContent = 'Error: ' + (data.error || 'Unknown error');
                        currentM3U8Url = '';
                    }
                })
                .catch(error => {
                    document.getElementById('modalTitle').textContent = channelName + ' - Error';
                    document.getElementById('modalUrl').textContent = 'Network error: ' + error.message;
                    currentM3U8Url = '';
                });
        }
        
        function copyModalUrl() {
            copyToClipboard(currentM3U8Url);
        }
        
        function openInVLC() {
            window.open('vlc://' + currentM3U8Url);
        }
        
        function closeModal() {
            document.getElementById('m3u8Modal').style.display = 'none';
        }
        
        function liveSearch(query) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (query.length > 0) {
                    window.location.href = '/?search=' + encodeURIComponent(query);
                }
            }, 1000);
        }
        
        // Close modal when clicking outside
        document.getElementById('m3u8Modal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
        
        // Auto-focus search box if coming from search
        <?php if ($searchQuery): ?>
        document.querySelector('.search-box').focus();
        <?php endif; ?>
    </script>
</body>
</html>
