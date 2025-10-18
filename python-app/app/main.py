"""
FastAPI main application
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.logger import setup_logging, get_logger
from app.core.cache import cache
from app.core.cookie_manager import cookie_manager
from app.core.playwright_service import playwright_service
from app.services.channel_service import channel_service

# Import routers
from app.api import routes, stream, playlist, proxy

# Setup logging
logger = setup_logging(
    level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    json_format=settings.LOG_JSON
)

app_logger = get_logger("main")


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


# Background task for cookie refresh
async def cookie_refresh_task():
    """Background task to refresh cookies periodically"""
    while True:
        try:
            await asyncio.sleep(300)  # Check every 5 minutes

            if await cookie_manager.should_refresh():
                app_logger.info("Triggering cookie refresh...")
                await cookie_manager.refresh_pool()

        except Exception as e:
            app_logger.error(f"Error in cookie refresh task: {e}")


# Background task for cache cleanup
async def cache_cleanup_task():
    """Background task to cleanup expired cache entries"""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            app_logger.debug("Running cache cleanup...")
            await cache.clear_expired()
        except Exception as e:
            app_logger.error(f"Error in cache cleanup task: {e}")


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    app_logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    try:
        # Initialize cache
        app_logger.info("Connecting to cache...")
        await cache.connect()

        # Load channels
        app_logger.info("Loading channels...")
        await channel_service.load_channels()

        # Start Playwright
        app_logger.info("Starting Playwright...")
        await playwright_service.start()

        # Initialize cookie manager
        app_logger.info("Initializing cookie manager...")
        await cookie_manager.initialize()

        # Start background tasks
        app_logger.info("Starting background tasks...")
        refresh_task = asyncio.create_task(cookie_refresh_task())
        cleanup_task = asyncio.create_task(cache_cleanup_task())

        app_logger.info(f"✓ {settings.APP_NAME} started successfully on {settings.base_url}")

        yield

        # Shutdown
        app_logger.info("Shutting down...")

        # Cancel background tasks
        refresh_task.cancel()
        cleanup_task.cancel()

        # Stop services
        await playwright_service.stop()
        await cache.disconnect()

        app_logger.info("Shutdown complete")

    except Exception as e:
        app_logger.error(f"Error during startup: {e}")
        raise


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ZEE5 Live TV Streaming Service with IPTV Support",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(routes.router, tags=["admin"])
app.include_router(stream.router, tags=["stream"])
app.include_router(playlist.router, tags=["playlist"])
app.include_router(proxy.router, tags=["proxy"])


# Homepage
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Homepage with channel list"""
    channels = channel_service.get_all_channels()
    cookie_status = cookie_manager.get_status()

    # Get dynamic base URL from request
    base_url = get_base_url_from_request(request)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "channels": channels,
            "cookie_status": cookie_status,
            "base_url": base_url,
            "total_channels": len(channels)
        }
    )


# Debug page
@app.get("/debug", response_class=HTMLResponse)
async def debug_page(request: Request):
    """Debug page with stream testing"""
    if not settings.ENABLE_DEBUG_ROUTES:
        return HTMLResponse(content="<h1>404 Not Found</h1>", status_code=404)

    channels = channel_service.get_all_channels()[:10]  # First 10 channels
    cookie_status = cookie_manager.get_status()

    # Get dynamic base URL from request
    base_url = get_base_url_from_request(request)

    return templates.TemplateResponse(
        "debug.html",
        {
            "request": request,
            "channels": channels,
            "cookie_status": cookie_status,
            "base_url": base_url
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
