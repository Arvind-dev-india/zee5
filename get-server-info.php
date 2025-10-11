<?php
// Get server configuration from environment or auto-detect
function getServerInfo() {
    // Try environment variables first
    $host = $_ENV['SERVER_HOST'] ?? getenv('SERVER_HOST');
    $port = $_ENV['SERVER_PORT'] ?? getenv('SERVER_PORT');
    
    // Auto-detect if not set
    if (!$host) {
        $host = $_SERVER['HTTP_HOST'] ?? 'localhost';
        // Remove port if it's in HTTP_HOST
        $host = explode(':', $host)[0];
    }
    
    if (!$port) {
        $port = $_SERVER['SERVER_PORT'] ?? '5052';
        // If we're behind a proxy, use the forwarded port
        if (isset($_SERVER['HTTP_X_FORWARDED_PORT'])) {
            $port = $_SERVER['HTTP_X_FORWARDED_PORT'];
        }
    }
    
    // Determine protocol
    $protocol = 'http://';
    if (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') {
        $protocol = 'https://';
    }
    if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
        $protocol = 'https://';
    }
    
    // Build base URL
    $baseUrl = $protocol . $host;
    if ($port != '80' && $port != '443') {
        $baseUrl .= ':' . $port;
    }
    
    return [
        'host' => $host,
        'port' => $port,
        'protocol' => $protocol,
        'base_url' => $baseUrl
    ];
}
?>