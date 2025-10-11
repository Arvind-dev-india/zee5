<?php
//=============================================================================//
// Get Stream URL API - Returns JSON with stream URL for AJAX calls
//=============================================================================//
header('Content-Type: application/json');
include_once '_functions.php';

$userAgent = $_SERVER['HTTP_USER_AGENT'] ?? "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";
$id = $_GET['id'] ?? null;

if (!$id) {
    echo json_encode(['error' => 'Channel ID is required']);
    exit;
}

function getCookieZee5Safe($userAgent) {
    $UAhash = md5($userAgent);
    $cacheFile = "tmp/cookie_z5_$UAhash.tmp";
    
    // Ensure tmp directory exists
    if (!file_exists(dirname($cacheFile))) {
        @mkdir(dirname($cacheFile), 0755, true);
    }
    
    $cacheExpiry = 43000; // 12 hours
    
    // Check cache first
    if (file_exists($cacheFile) && (time() - filemtime($cacheFile) < $cacheExpiry)) {
        $cookie = file_get_contents($cacheFile);
        if ($cookie) {
            $remaining = $cacheExpiry - (time() - filemtime($cacheFile));
            return [
                'cookie' => $cookie,
                'cached' => true,
                'expires_in' => $remaining
            ];
        }
    }
    
    // Generate new cookie
    try {
        $result = generateCookieZee5($userAgent);
        if (isset($result['cookie']) && $result['cookie']) {
            // Try to save to cache
            @file_put_contents($cacheFile, $result['cookie']);
            return [
                'cookie' => $result['cookie'],
                'cached' => false,
                'expires_in' => $cacheExpiry
            ];
        }
    } catch (Exception $e) {
        return ['error' => 'Failed to generate authentication: ' . $e->getMessage()];
    }
    
    return ['error' => 'Unable to generate authentication token'];
}

// Load channel data
$file = 'data.json';
$json_data = file_get_contents($file);
if ($json_data === false) {
    echo json_encode(['error' => 'Channel data not found']);
    exit;
}

$data = json_decode($json_data, true);
$channelData = null;
foreach ($data['data'] as $channel) {
    if ($channel['id'] == $id) {
        $channelData = $channel;
        break;
    }
}

if ($channelData === null) {
    echo json_encode(['error' => 'Channel not found']);
    exit;
}

// Generate stream URL
$cookieResult = getCookieZee5Safe($userAgent);
if (isset($cookieResult['error'])) {
    echo json_encode($cookieResult);
    exit;
}

$streamUrl = $channelData['url'] . '?' . $cookieResult['cookie'];

echo json_encode([
    'success' => true,
    'channel' => [
        'id' => $channelData['id'],
        'name' => $channelData['name'],
        'genre' => $channelData['genre'],
        'language' => $channelData['language']
    ],
    'stream_url' => $streamUrl,
    'base_url' => $channelData['url'],
    'cached' => $cookieResult['cached'],
    'expires_in' => $cookieResult['expires_in']
]);
?>