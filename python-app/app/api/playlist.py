"""
M3U Playlist generation endpoint
"""
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from datetime import datetime
from urllib.parse import quote

from app.config import settings
from app.services.channel_service import channel_service
from app.utils.helpers import generate_user_agent
from app.utils.logger import get_logger

logger = get_logger("api.playlist")

router = APIRouter()


def get_base_url_from_request(request: Request) -> str:
    """
    Get the base URL from request headers (for dynamic URL generation)
    Falls back to SERVER_URL if configured, or constructs from request
    """
    # If SERVER_URL is set and not 0.0.0.0, use it
    if settings.SERVER_URL and "0.0.0.0" not in settings.SERVER_URL:
        return settings.SERVER_URL

    # Otherwise, build from request headers
    scheme = request.url.scheme or "http"
    host = request.headers.get("host") or f"{settings.HOST}:{settings.PORT}"

    # If host is 0.0.0.0, try to use X-Forwarded-Host or fall back to SERVER_URL
    if "0.0.0.0" in host:
        forwarded_host = request.headers.get("x-forwarded-host")
        if forwarded_host:
            host = forwarded_host
        elif settings.SERVER_URL:
            return settings.SERVER_URL

    return f"{scheme}://{host}"


@router.get("/playlist.m3u", response_class=PlainTextResponse)
@router.get("/playlist.php", response_class=PlainTextResponse)
async def get_m3u_playlist(request: Request):
    """
    Generate M3U8 playlist for IPTV players

    Returns:
        M3U8 playlist as plain text
    """
    try:
        channels = channel_service.get_all_channels()
        user_agent = generate_user_agent()

        # Get the correct base URL from the request
        base_url = get_base_url_from_request(request)

        # Build M3U8 playlist
        lines = ["#EXTM3U"]

        # Add header info
        lines.append(f"#EXTINF:-1 tvg-id=\"\" tvg-name=\"ZEE5 Playlist\" tvg-logo=\"\" group-title=\"INFO\",ZEE5 Streaming Server - {len(channels)} Channels")
        lines.append(f"# Server: {base_url}")
        lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"# Total Channels: {len(channels)}")
        lines.append("")

        # Add channels
        for channel in channels:
            display_name = f"{channel.name} [{channel.language.upper()}]"

            # Channel metadata
            lines.append(
                f"#EXTINF:-1 "
                f'tvg-id="{channel.id}" '
                f'tvg-name="{channel.name}" '
                f'tvg-logo="{channel.logo}" '
                f'tvg-chno="{channel.chno}" '
                f'tvg-country="{channel.country}" '
                f'tvg-language="{channel.language}" '
                f'group-title="{channel.genre}",'
                f'{display_name}'
            )

            # Kodi properties
            lines.append("#KODIPROP:inputstream=inputstream.adaptive")
            lines.append("#KODIPROP:inputstream.adaptive.manifest_type=HLS")
            lines.append(f"#KODIPROP:inputstream.adaptive.manifest_headers=User-Agent={quote(user_agent)}")
            lines.append(f"#KODIPROP:inputstream.adaptive.stream_headers=User-Agent={quote(user_agent)}")

            # VLC options
            lines.append(f"#EXTVLCOPT:http-user-agent={user_agent}")

            # Stream URL with dynamic base URL
            stream_url = f"{base_url}/stream?id={quote(channel.id)}"
            lines.append(stream_url)
            lines.append("")

        # Add footer
        lines.append("# End of playlist")
        lines.append("# For support visit: https://t.me/ygxworld")
        lines.append("# Educational use only")

        playlist = "\n".join(lines)

        logger.info(f"Generated M3U playlist with {len(channels)} channels")

        return playlist

    except Exception as e:
        logger.error(f"Error generating playlist: {e}")
        return f"#EXTM3U\n# Error: {str(e)}"
