<?php
//=============================================================================//
// FOR EDUCATION PURPOSE ONLY. Don't Sell this Script, This is 100% Free.
// Join Community https://t.me/ygxworld, https://t.me/ygx_chat
//=============================================================================//
include_once '_functions.php';

// Use a more realistic browser user agent
$userAgent = $_SERVER['HTTP_USER_AGENT'] ?? "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";

$id = $_GET['id'] ?? null;
if (!$id) {
    http_response_code(400);
    die("Channel id not found in query parameter.");
}

function getCookieZee5($userAgent) {
    $UAhash = md5($userAgent);
    $cacheFile = "tmp/cookie_z5_$UAhash.tmp";
    
    // Ensure tmp directory exists with proper permissions
    if (!file_exists(dirname($cacheFile))) {
        mkdir(dirname($cacheFile), 0755, true);
    }
    
    $cacheExpiry = 43000; // 12 hour
    if (file_exists($cacheFile) && (time() - filemtime($cacheFile) < $cacheExpiry)) {
        return file_get_contents($cacheFile);
    }
    
    // Generate new cookie
    $data = generateCookieZee5($userAgent);
    if (isset($data['cookie'])) {
        // Try to save the cookie, but don't fail if we can't
        $result = @file_put_contents($cacheFile, $data['cookie']);
        if ($result === false) {
            // If we can't save to file, just return the cookie without caching
            error_log("Warning: Could not save cookie to cache file: $cacheFile");
        }
        return $data['cookie'];
    }
    
    return null;
}

// Load channel data
$file = 'data.json';
$json_data = file_get_contents($file);

if ($json_data === false) {
    http_response_code(500);
    die('data.json file not found.');
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
    http_response_code(404);
    die('Channel not found.');
}

// Get the streaming URL
$initialUrl = $channelData['url'];
$cookie = getCookieZee5($userAgent);

if (!$cookie) {
    http_response_code(500);
    die('Unable to generate authentication cookie. The service may be temporarily unavailable.');
}

// Redirect to the streaming URL with authentication
header("Location: $initialUrl?$cookie", true, 302);
exit;

//@yuvraj824