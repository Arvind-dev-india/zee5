<?php
//=============================================================================//
// DEBUG VERSION - Shows detailed information about streaming process
//=============================================================================//
include_once '_functions.php';

// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 1);

$userAgent = $_SERVER['HTTP_USER_AGENT'] ?? "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";
$id = $_GET['id'] ?? '0-9-zeetamil'; // Default channel for testing

echo "<h2>🔍 ZEE5 Streaming Debug Information</h2>";
echo "<p><strong>Channel ID:</strong> $id</p>";
echo "<p><strong>User Agent:</strong> " . htmlspecialchars($userAgent) . "</p>";

// Check tmp directory permissions
echo "<h3>📁 Directory Permissions</h3>";
$tmpDir = "tmp";
if (file_exists($tmpDir)) {
    $perms = fileperms($tmpDir);
    echo "<p><strong>tmp/ directory permissions:</strong> " . sprintf('%o', $perms) . "</p>";
    echo "<p><strong>tmp/ is writable:</strong> " . (is_writable($tmpDir) ? "✅ Yes" : "❌ No") . "</p>";
} else {
    echo "<p>❌ tmp/ directory does not exist</p>";
}

// Load channel data
echo "<h3>📺 Channel Data</h3>";
$file = 'data.json';
$json_data = file_get_contents($file);
if ($json_data === false) {
    echo "<p>❌ Error: data.json file not found</p>";
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
    echo "<p>❌ Error: Channel '$id' not found</p>";
    echo "<p><strong>Available channels:</strong></p><ul>";
    foreach (array_slice($data['data'], 0, 5) as $ch) {
        echo "<li>" . htmlspecialchars($ch['id']) . " - " . htmlspecialchars($ch['name']) . "</li>";
    }
    echo "</ul>";
    exit;
}

echo "<p>✅ Channel found: " . htmlspecialchars($channelData['name']) . "</p>";
echo "<p><strong>Base URL:</strong> " . htmlspecialchars($channelData['url']) . "</p>";

// Test cookie generation
echo "<h3>🍪 Cookie Generation</h3>";
try {
    $UAhash = md5($userAgent);
    $cacheFile = "tmp/cookie_z5_$UAhash.tmp";
    echo "<p><strong>Cache file:</strong> $cacheFile</p>";
    
    // Check if cache file exists and is valid
    $cacheExpiry = 43000; // 12 hours
    if (file_exists($cacheFile) && (time() - filemtime($cacheFile) < $cacheExpiry)) {
        $cookie = file_get_contents($cacheFile);
        $remaining = $cacheExpiry - (time() - filemtime($cacheFile));
        echo "<p>✅ Using cached cookie (expires in " . round($remaining/3600, 1) . " hours)</p>";
        echo "<p><strong>Cookie preview:</strong> " . htmlspecialchars(substr($cookie, 0, 100)) . "...</p>";
    } else {
        echo "<p>🔄 Generating new cookie...</p>";
        echo "<p><em>This may take a few seconds...</em></p>";
        
        // Try to generate new cookie
        $result = generateCookieZee5($userAgent);
        if (isset($result['cookie'])) {
            $cookie = $result['cookie'];
            echo "<p>✅ Cookie generated successfully</p>";
            echo "<p><strong>Cookie preview:</strong> " . htmlspecialchars(substr($cookie, 0, 100)) . "...</p>";
            
            // Try to save cookie
            $saveResult = @file_put_contents($cacheFile, $cookie);
            if ($saveResult === false) {
                echo "<p>⚠️ Warning: Could not save cookie to cache (will work but won't be cached)</p>";
            } else {
                echo "<p>✅ Cookie saved to cache</p>";
            }
        } else {
            echo "<p>❌ Error: Could not generate cookie</p>";
            if (isset($result['error'])) {
                echo "<p><strong>Error details:</strong> " . htmlspecialchars($result['error']) . "</p>";
            }
            exit;
        }
    }
    
    // Generate final URL
    $finalUrl = $channelData['url'] . '?' . $cookie;
    echo "<h3>🎬 Final Stream URL</h3>";
    echo "<p><strong>Complete URL:</strong> <code>" . htmlspecialchars($finalUrl) . "</code></p>";
    
    // Test URL accessibility
    echo "<h3>🌐 URL Accessibility Test</h3>";
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $finalUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_NOBODY, true); // HEAD request only
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'User-Agent: ' . $userAgent
    ]);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);
    
    if ($error) {
        echo "<p>❌ cURL Error: " . htmlspecialchars($error) . "</p>";
    } else {
        echo "<p><strong>HTTP Response Code:</strong> $httpCode</p>";
        if ($httpCode == 200) {
            echo "<p>✅ Stream URL is accessible</p>";
        } elseif ($httpCode >= 300 && $httpCode < 400) {
            echo "<p>🔄 Stream URL redirects (this is normal)</p>";
        } else {
            echo "<p>❌ Stream URL returned error code</p>";
        }
    }
    
    echo "<h3>🎯 Usage Instructions</h3>";
    echo "<p><strong>For VLC:</strong> Copy the complete URL above and paste it in VLC (Media → Open Network Stream)</p>";
    echo "<p><strong>For IPTV Apps:</strong> Use the individual stream URL or the M3U playlist</p>";
    echo "<p><strong>Direct Link:</strong> <a href='" . htmlspecialchars($finalUrl) . "' target='_blank'>Click to test stream</a></p>";
    
} catch (Exception $e) {
    echo "<p>❌ Exception: " . htmlspecialchars($e->getMessage()) . "</p>";
}

echo "<hr>";
echo "<p><a href='/'>&larr; Back to Homepage</a> | <a href='/stream.php?id=$id'>Try Normal Stream</a></p>";
?>