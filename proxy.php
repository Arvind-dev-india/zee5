<?php
//=============================================================================//
// HLS Proxy - Streams content from ZEE5 CDN through our server
// FOR EDUCATION PURPOSE ONLY
//=============================================================================//

// Get parameters
$url = $_GET['url'] ?? null;
$type = $_GET['type'] ?? 'master'; // master, variant, or segment

if (!$url) {
    http_response_code(400);
    die("URL parameter required");
}

// Decode the URL
$url = base64_decode($url);

// Get user agent from request or use default
$userAgent = $_SERVER['HTTP_USER_AGENT'] ?? "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";

// Initialize curl
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_USERAGENT, $userAgent);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);

// Set headers
$headers = [
    'Accept: */*',
    'Accept-Language: en-US,en;q=0.9',
    'Origin: https://www.zee5.com',
    'Referer: https://www.zee5.com/',
];
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

// Get the content
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$contentType = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
curl_close($ch);

if ($response === false || $httpCode !== 200) {
    http_response_code($httpCode ?: 500);
    die("Failed to fetch content from CDN");
}

// Handle different types
if ($type === 'segment') {
    // For TS segments, just stream directly
    header('Content-Type: ' . ($contentType ?: 'video/MP2T'));
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, OPTIONS');
    header('Access-Control-Allow-Headers: *');
    header('Cache-Control: public, max-age=3600');
    echo $response;
    exit;
}

// For playlists (master or variant), rewrite URLs
if ($type === 'master' || $type === 'variant') {
    $lines = explode("\n", $response);
    $baseUrl = dirname($url) . '/';

    // Get current script info
    include_once 'get-server-info.php';
    $serverInfo = getServerInfo();
    $proxyUrl = $serverInfo['base_url'] . '/proxy.php';

    $output = [];
    foreach ($lines as $line) {
        $line = trim($line);

        // Skip empty lines and comments (except #EXTM3U and other tags)
        if (empty($line)) {
            $output[] = '';
            continue;
        }

        if ($line[0] === '#') {
            $output[] = $line;
            continue;
        }

        // This is a URL line - rewrite it
        $originalUrl = $line;

        // Make absolute URL if relative
        if (!preg_match('/^https?:\/\//', $originalUrl)) {
            $originalUrl = $baseUrl . $originalUrl;
        }

        // Determine the type for this URL
        $nextType = 'variant';
        if (strpos($originalUrl, '.ts') !== false || strpos($originalUrl, '.m4s') !== false) {
            $nextType = 'segment';
        }

        // Create proxied URL
        $encodedUrl = base64_encode($originalUrl);
        $proxiedUrl = $proxyUrl . '?url=' . urlencode($encodedUrl) . '&type=' . $nextType;

        $output[] = $proxiedUrl;
    }

    // Send playlist
    header('Content-Type: application/vnd.apple.mpegurl');
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, OPTIONS');
    header('Access-Control-Allow-Headers: *');
    header('Cache-Control: no-cache');

    echo implode("\n", $output);
    exit;
}

// Default fallback
header('Content-Type: text/plain');
echo $response;
?>
