"""
HLS Proxy API endpoints - Streams content from ZEE5 CDN through our server
"""
import base64
import re
from typing import Optional
from urllib.parse import urljoin, urlparse, quote, unquote

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, Response

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("api.proxy")

router = APIRouter()

# HTTP client with appropriate timeouts
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0, connect=10.0),
    follow_redirects=True,
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
)


def get_base_url(request: Request) -> str:
    """Get the base URL for this server"""
    # Use SERVER_URL from settings if available
    if hasattr(settings, 'SERVER_URL') and settings.SERVER_URL:
        return settings.SERVER_URL.rstrip('/')

    # Fallback to request info
    scheme = request.url.scheme
    host = request.headers.get("host", "localhost:5052")
    return f"{scheme}://{host}"


def rewrite_playlist(content: str, original_url: str, proxy_base_url: str) -> str:
    """
    Rewrite URLs in HLS playlist to point to our proxy

    Args:
        content: Playlist content
        original_url: Original URL of the playlist
        proxy_base_url: Base URL of our proxy endpoint

    Returns:
        Rewritten playlist content
    """
    lines = content.split('\n')
    base_url = original_url.rsplit('/', 1)[0] + '/'
    output_lines = []

    for line in lines:
        line = line.rstrip()

        # Empty line
        if not line:
            output_lines.append('')
            continue

        # Comment line (keep as is)
        if line.startswith('#'):
            output_lines.append(line)
            continue

        # This is a URL line - rewrite it
        original_line_url = line

        # Make absolute URL if relative
        if not re.match(r'^https?://', original_line_url):
            absolute_url = urljoin(base_url, original_line_url)
        else:
            absolute_url = original_line_url

        # Determine the type
        url_type = 'variant'
        if '.ts' in absolute_url.lower() or '.m4s' in absolute_url.lower():
            url_type = 'segment'

        # Create proxied URL
        encoded_url = base64.b64encode(absolute_url.encode()).decode()
        proxied_url = f"{proxy_base_url}/proxy?url={quote(encoded_url)}&type={url_type}"

        output_lines.append(proxied_url)

    return '\n'.join(output_lines)


@router.get("/proxy")
async def hls_proxy(
    request: Request,
    url: str = Query(..., description="Base64 encoded URL to proxy"),
    type: str = Query(default="master", description="Content type: master, variant, or segment")
):
    """
    Proxy HLS content from ZEE5 CDN

    Args:
        url: Base64 encoded URL to fetch
        type: Type of content (master playlist, variant playlist, or segment)

    Returns:
        Proxied content with rewritten URLs for playlists
    """
    try:
        # Decode the URL
        try:
            decoded_url = base64.b64decode(unquote(url)).decode()
        except Exception as e:
            logger.error(f"Failed to decode URL: {e}")
            raise HTTPException(status_code=400, detail="Invalid URL encoding")

        logger.info(f"Proxying {type} content from: {decoded_url[:100]}...")

        # Get user agent from request or use default
        user_agent = request.headers.get(
            "user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Prepare headers for CDN request
        headers = {
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://www.zee5.com",
            "Referer": "https://www.zee5.com/",
        }

        # Fetch content from CDN
        try:
            response = await http_client.get(decoded_url, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch from CDN: {e}")
            raise HTTPException(status_code=502, detail=f"Failed to fetch content from CDN: {str(e)}")

        content = response.content
        content_type = response.headers.get("content-type", "")

        # For segments, stream directly
        if type == "segment":
            logger.debug(f"Streaming segment directly")
            return Response(
                content=content,
                media_type=content_type or "video/MP2T",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                    "Cache-Control": "public, max-age=3600",
                }
            )

        # For playlists, rewrite URLs
        if type in ("master", "variant"):
            try:
                playlist_content = content.decode('utf-8')

                # Get proxy base URL
                proxy_base_url = get_base_url(request)

                # Rewrite playlist
                rewritten_playlist = rewrite_playlist(
                    playlist_content,
                    decoded_url,
                    proxy_base_url
                )

                logger.debug(f"Rewritten {type} playlist")

                return Response(
                    content=rewritten_playlist,
                    media_type="application/vnd.apple.mpegurl",
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                        "Cache-Control": "no-cache",
                    }
                )
            except Exception as e:
                logger.error(f"Failed to rewrite playlist: {e}")
                # If rewriting fails, return original content
                return Response(
                    content=content,
                    media_type="application/vnd.apple.mpegurl"
                )

        # Default fallback
        return Response(content=content, media_type=content_type or "text/plain")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in HLS proxy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")
