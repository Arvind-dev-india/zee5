<?php
//=============================================================================//
// THIS SCRIPT IS FOR EDUCATION PURPOSE ONLY. Don't Sell this Script.
// Join Community https://t.me/ygxworld, https://t.me/ygx_chat
//=============================================================================//

include_once 'get-server-info.php';

$jsonFile = 'data.json';
$jsonData = file_get_contents($jsonFile);
$serverInfo = getServerInfo();
$scriptUrl = rtrim($serverInfo['base_url'], '/') . '/stream.php';
$data = json_decode($jsonData, true);

function getUserAgent() {
    $uaFile = 'useragent';

    if (file_exists($uaFile)) {
        return trim(file_get_contents($uaFile));
    }

    $chromeVersions = range(120, 131);
    $edgeVersions = range(120, 131);
    $safariVersions = ['16.6', '17.0', '17.1', '17.2', '17.3', '17.4', '17.5', '17.6', '18.0'];
    $webkitVersions = range(605, 620);

    $userAgents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" . $chromeVersions[array_rand($chromeVersions)] . ".0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" . $chromeVersions[array_rand($chromeVersions)] . ".0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" . $chromeVersions[array_rand($chromeVersions)] . ".0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" . $edgeVersions[array_rand($edgeVersions)] . ".0.0.0 Safari/537.36 Edg/" . $edgeVersions[array_rand($edgeVersions)] . ".0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/" . $webkitVersions[array_rand($webkitVersions)] . ".1.15 (KHTML, like Gecko) Version/" . $safariVersions[array_rand($safariVersions)] . " Safari/" . $webkitVersions[array_rand($webkitVersions)] . ".1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0"
    ];

    $selectedUA = $userAgents[array_rand($userAgents)];
    @file_put_contents($uaFile, $selectedUA);

    return $selectedUA;
}

$countries = !empty($_GET['country']) ? array_map('strtolower', explode(',', $_GET['country'])) : [];
$languages = !empty($_GET['language']) ? array_map('strtolower', explode(',', $_GET['language'])) : [];

// Set content type for M3U playlist
header('Content-Type: application/vnd.apple.mpegurl');
header('Content-Disposition: attachment; filename="zee5_channels.m3u"');

echo "#EXTM3U\n";
echo "#EXTINF:-1 tvg-id=\"\" tvg-name=\"ZEE5 Playlist\" tvg-logo=\"\" group-title=\"INFO\",ZEE5 Streaming Server - " . count($data['data']) . " Channels\n";
echo "# Server: " . $serverInfo['base_url'] . "\n";
echo "# Generated: " . date('Y-m-d H:i:s') . "\n";
echo "# Total Channels: " . count($data['data']) . "\n";
echo "\n";

$userAgent = getUserAgent();
$seenIds = [];

foreach ($data['data'] as $channel) {
    $id = $channel['id'] ?? '';
    if ($id === '' || isset($seenIds[$id])) continue;

    $country = strtolower($channel['country'] ?? '');
    $language = strtolower($channel['language'] ?? '');
    if (($countries && !in_array($country, $countries)) || ($languages && !in_array($language, $languages))) continue;

    $seenIds[$id] = true;

    $chno      = $channel['chno'] ?? '';
    $name      = $channel['name'] ?? '';
    $logo      = $channel['logo'] ?? '';
    $genre     = $channel['genre'] ?? '';

    echo "#EXTINF:-1 tvg-id=\"$id\" tvg-country=\"$country\" tvg-chno=\"$chno\" tvg-language=\"$language\" tvg-name=\"$name\" tvg-logo=\"$logo\" group-title=\"$genre\", $name\n";
    echo "#KODIPROP:inputstream=inputstream.adaptive\n";
    echo "#KODIPROP:inputstream.adaptive.manifest_type=HLS\n";
    echo "#KODIPROP:inputstream.adaptive.manifest_headers=User-Agent=".urlencode($userAgent)."\n";
    echo "#KODIPROP:inputstream.adaptive.stream_headers=User-Agent=".urlencode($userAgent)."\n";
    echo "#EXTVLCOPT:http-user-agent=$userAgent\n";
    echo $scriptUrl . '?id=' . urlencode($id) . "&%7CUser-Agent=" . urlencode($userAgent) . "\n\n";
}

// Footer comments
echo "\n# End of playlist\n";
echo "# For support visit: https://t.me/ygxworld\n";
echo "# Educational use only\n";
exit;

