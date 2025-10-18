"""
Admin and health check API routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.models import HealthResponse
from app.config import settings
from app.core.cookie_manager import cookie_manager
from app.core.cache import cache
from app.services.channel_service import channel_service
from app.utils.logger import get_logger

logger = get_logger("api.routes")

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
@router.head("/health")
async def health_check():
    """
    Health check endpoint

    Returns service status and component health
    """
    services = {
        "cache": "unknown",
        "channels": "unknown",
        "cookie_manager": "unknown"
    }

    # Check cache
    try:
        if cache._connected or (await cache.exists("test")):
            services["cache"] = "healthy"
        else:
            services["cache"] = "file_only"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        services["cache"] = "unhealthy"

    # Check channels
    try:
        if len(channel_service.channels) > 0:
            services["channels"] = "healthy"
        else:
            services["channels"] = "not_loaded"
    except Exception as e:
        logger.error(f"Channel service health check failed: {e}")
        services["channels"] = "unhealthy"

    # Check cookie manager
    try:
        cookie_status = cookie_manager.get_status()
        if cookie_status.valid_cookies > 0:
            services["cookie_manager"] = "healthy"
        else:
            services["cookie_manager"] = "no_valid_cookies"
    except Exception as e:
        logger.error(f"Cookie manager health check failed: {e}")
        services["cookie_manager"] = "unhealthy"

    # Overall status
    overall_status = "healthy"
    if any(status in ["unhealthy", "not_loaded", "no_valid_cookies"] for status in services.values()):
        overall_status = "degraded"

    cookie_pool_info = cookie_manager.get_status().dict() if cookie_manager else {}

    return HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.now(),
        services=services,
        cookie_pool=cookie_pool_info
    )


@router.get("/cookie/status")
async def cookie_status():
    """Get detailed cookie pool status"""
    try:
        status = cookie_manager.get_status()
        return status.dict()
    except Exception as e:
        logger.error(f"Error getting cookie status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cookie/refresh")
async def refresh_cookies():
    """Manually trigger cookie pool refresh"""
    try:
        logger.info("Manual cookie refresh triggered")
        await cookie_manager.refresh_pool()
        status = cookie_manager.get_status()
        return {
            "success": True,
            "message": "Cookie pool refreshed",
            "status": status.dict()
        }
    except Exception as e:
        logger.error(f"Cookie refresh failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channels/stats")
async def channel_stats():
    """Get channel statistics"""
    try:
        channels = channel_service.get_all_channels()

        return {
            "total_channels": len(channels),
            "genres": channel_service.get_genres(),
            "languages": channel_service.get_languages(),
            "countries": channel_service.get_countries()
        }
    except Exception as e:
        logger.error(f"Error getting channel stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/info")
async def debug_info():
    """Get debug information (only if DEBUG enabled)"""
    if not settings.ENABLE_DEBUG_ROUTES:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "redis_enabled": settings.USE_REDIS,
        "cache_dir": settings.CACHE_DIR,
        "cookie_pool_size": settings.COOKIE_POOL_SIZE,
        "base_url": settings.base_url
    }
