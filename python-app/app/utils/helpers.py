"""
Helper utility functions
"""
import re
import random
import base64
import json
from typing import Dict, Any


def base64_url_encode(data: bytes) -> str:
    """
    Base64 URL-safe encoding (without padding)

    Args:
        data: Bytes to encode

    Returns:
        Base64 URL-safe encoded string
    """
    encoded = base64.b64encode(data).decode('utf-8')
    # Replace + with -, / with _, and remove = padding
    encoded = encoded.replace('+', '-').replace('/', '_').rstrip('=')
    return encoded


def generate_jwt_token(payload: Dict[str, Any]) -> str:
    """
    Generate JWT token for ZEE5 (unsigned, alg=none)

    Args:
        payload: Token payload dictionary

    Returns:
        JWT token string
    """
    header = {"alg": "none", "typ": "JWT"}

    # Use separators to create compact JSON without spaces (matching PHP behavior)
    header_encoded = base64_url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_encoded = base64_url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))

    return f"{header_encoded}.{payload_encoded}."


def generate_guest_token() -> str:
    """
    Generate a random guest token (UUID v4-like format)

    Returns:
        Guest token string
    """
    hex_chars = '0123456789abcdef'
    segments = [8, 4, 4, 4, 12]

    token_parts = []
    for length in segments:
        segment = ''.join(random.choice(hex_chars) for _ in range(length))
        token_parts.append(segment)

    return '-'.join(token_parts)


def generate_user_agent() -> str:
    """
    Generate a random realistic user agent

    Returns:
        User agent string
    """
    chrome_versions = list(range(120, 132))
    edge_versions = list(range(120, 132))
    safari_versions = ['16.6', '17.0', '17.1', '17.2', '17.3', '17.4', '17.5', '17.6', '18.0']
    webkit_versions = list(range(605, 621))

    user_agents = [
        # Chrome on Windows
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(chrome_versions)}.0.0.0 Safari/537.36",
        # Chrome on macOS
        f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(chrome_versions)}.0.0.0 Safari/537.36",
        # Chrome on Linux
        f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(chrome_versions)}.0.0.0 Safari/537.36",
        # Edge on Windows
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(edge_versions)}.0.0.0 Safari/537.36 Edg/{random.choice(edge_versions)}.0.0.0",
        # Safari on macOS
        f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/{random.choice(webkit_versions)}.1.15 (KHTML, like Gecko) Version/{random.choice(safari_versions)} Safari/{random.choice(webkit_versions)}.1.15",
    ]

    return random.choice(user_agents)


def clean_url(url: str) -> str:
    """
    Clean and validate URL

    Args:
        url: URL to clean

    Returns:
        Cleaned URL
    """
    url = url.strip()
    # Remove any whitespace
    url = re.sub(r'\s+', '', url)
    return url


def extract_cookie_from_m3u8(content: str) -> str:
    """
    Extract hdntl cookie from M3U8 content

    Args:
        content: M3U8 file content

    Returns:
        Cookie string (hdntl=...)
    """
    match = re.search(r'hdntl=([^,\s&]+)', content)
    if match:
        return f"hdntl={match.group(1)}"
    raise ValueError("Cookie not found in M3U8 content")


def format_time_remaining(seconds: int) -> str:
    """
    Format seconds into human-readable time

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    if seconds < 0:
        return "Expired"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"
