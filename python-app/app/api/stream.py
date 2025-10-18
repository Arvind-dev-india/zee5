"""
Stream API endpoints
"""
import base64
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, PlainTextResponse

from app.services.stream_service import stream_service
from app.services.channel_service import channel_service
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("api.stream")

router = APIRouter()


def get_base_url_from_request(request: Request) -> str:
    """Get the base URL from request"""
    if settings.SERVER_URL and "0.0.0.0" not in settings.SERVER_URL:
        return settings.SERVER_URL.rstrip('/')

    scheme = request.url.scheme or "http"
    host = request.headers.get("host") or f"{settings.HOST}:{settings.PORT}"

    if "0.0.0.0" in host:
        forwarded_host = request.headers.get("x-forwarded-host")
        if forwarded_host:
            host = forwarded_host
        elif settings.SERVER_URL:
            return settings.SERVER_URL.rstrip('/')

    return f"{scheme}://{host}"


@router.get("/stream")
async def get_stream(
    request: Request,
    id: str = Query(..., description="Channel ID"),
    format: str = Query(default="redirect", description="Response format: redirect, url, or hls")
):
    """
    Get stream URL for a channel

    Args:
        id: Channel ID
        format: Response format (redirect, url, or hls)

    Returns:
        Redirect to stream URL, plain text URL, or HLS proxy URL
    """
    try:
        user_agent = request.headers.get("user-agent", "")

        # Get stream URL
        response = await stream_service.get_stream_url(id, user_agent)

        if not response.success:
            raise HTTPException(status_code=404, detail=response.error or "Stream not found")

        # Check format preference - for VLC/media players or explicit url format request
        if format == "url" or "vlc" in user_agent.lower() or "mplayer" in user_agent.lower():
            # Return direct CDN URL as plain text for media players (matching PHP)
            return PlainTextResponse(content=response.stream_url)

        # Default: redirect directly to CDN URL (matching PHP for browsers)
        # The stream_url already has the cookie appended
        return RedirectResponse(url=response.stream_url, status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in stream endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/get-stream-url")
async def get_stream_url_api(
    id: str = Query(..., description="Channel ID")
):
    """
    Get stream URL as JSON (for AJAX calls)

    Args:
        id: Channel ID

    Returns:
        JSON with stream URL and metadata
    """
    try:
        response = await stream_service.get_stream_url(id)

        if not response.success:
            return {
                "success": False,
                "error": response.error or "Failed to get stream URL"
            }

        return {
            "success": True,
            "channel": {
                "id": response.channel.id,
                "name": response.channel.name,
                "genre": response.channel.genre,
                "language": response.channel.language
            } if response.channel else None,
            "stream_url": response.stream_url,
            "base_url": response.channel.url if response.channel else None,
            "cached": response.cached,
            "expires_in": response.expires_in
        }

    except Exception as e:
        logger.error(f"Error in get-stream-url API: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/channels")
async def list_channels(
    search: str = Query(default="", description="Search query"),
    genre: str = Query(default=None, description="Filter by genre"),
    language: str = Query(default=None, description="Filter by language"),
    country: str = Query(default=None, description="Filter by country")
):
    """
    List all channels with optional filters

    Args:
        search: Search query
        genre: Filter by genre
        language: Filter by language
        country: Filter by country

    Returns:
        List of channels
    """
    try:
        channels = channel_service.search_channels(
            query=search,
            genre=genre,
            language=language,
            country=country
        )

        return {
            "total": len(channels),
            "channels": [channel.dict() for channel in channels]
        }

    except Exception as e:
        logger.error(f"Error listing channels: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
