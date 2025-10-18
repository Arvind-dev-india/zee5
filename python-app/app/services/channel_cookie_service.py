"""
Per-channel cookie service with Redis caching
Generates channel-specific authentication cookies on-demand
"""
import httpx
import re
from datetime import datetime, timedelta

from app.config import settings
from app.core.cache import cache
from app.core.token_generator import TokenGenerator
from app.core.playwright_service import playwright_service
from app.utils.logger import get_logger
from app.utils.helpers import generate_user_agent

logger = get_logger("channel_cookie_service")


class ChannelCookieService:
    """Service for generating and caching per-channel cookies"""

    def __init__(self):
        self.token_generator = TokenGenerator()

    async def get_channel_cookie(self, channel_id: str) -> str:
        """
        Get a cookie for a specific channel (with caching)

        Args:
            channel_id: Channel ID to get cookie for

        Returns:
            Cookie string (hdntl=...)
        """
        # Check cache first
        cache_key = f"channel_cookie:{channel_id}"
        cached_cookie = await cache.get(cache_key)

        if cached_cookie:
            logger.debug(f"Using cached cookie for channel {channel_id}")
            return cached_cookie.decode() if isinstance(cached_cookie, bytes) else cached_cookie

        # Generate new cookie
        logger.info(f"Generating new cookie for channel {channel_id}")
        cookie = await self._generate_channel_cookie(channel_id)

        # Cache for 10 hours (36000 seconds)
        await cache.set(cache_key, cookie, ttl=36000)

        return cookie

    async def _generate_channel_cookie(self, channel_id: str) -> str:
        """
        Generate a new cookie for a specific channel

        Args:
            channel_id: Channel ID

        Returns:
            Cookie string
        """
        # Use fixed user agent matching PHP version
        from app.config import settings
        user_agent = settings.DEFAULT_USER_AGENT

        try:
            # Step 1: Get platform token (cached)
            platform_token = await self._get_cached_platform_token()

            # Step 2: Generate guest and DD tokens
            guest_token = self.token_generator.generate_guest_token()
            dd_token = self.token_generator.generate_dd_token()

            # Step 3: Get M3U8 URL from ZEE5 API for THIS specific channel
            logger.debug(f"Fetching M3U8 URL for channel {channel_id}...")
            url = (
                f"{settings.ZEE5_API_URL}/singlePlayback/getDetails/secure"
                f"?channel_id={channel_id}&device_id={guest_token}"
                f"&platform_name=desktop_web&translation=en&user_language=en,hi"
                f"&country=IN&state=&app_version=4.24.0&user_type=guest"
                f"&check_parental_control=false"
            )

            headers = self.token_generator.get_api_headers(
                platform_token, guest_token, dd_token, user_agent
            )

            payload = self.token_generator.get_api_payload(
                platform_token, guest_token, dd_token
            )

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)

                logger.debug(f"API response status: {response.status_code}")
                logger.debug(f"API response body: {response.text[:500]}")

                if response.status_code == 401:
                    # Platform token might be expired, get a new one
                    logger.warning("Got 401, fetching fresh platform token...")
                    await cache.delete("platform_token")
                    platform_token = await self._get_cached_platform_token()

                    # Retry with new token
                    headers = self.token_generator.get_api_headers(
                        platform_token, guest_token, dd_token, user_agent
                    )
                    payload = self.token_generator.get_api_payload(
                        platform_token, guest_token, dd_token
                    )
                    response = await client.post(url, headers=headers, json=payload)
                    logger.debug(f"Retry API response status: {response.status_code}")
                    logger.debug(f"Retry API response body: {response.text[:500]}")

                response.raise_for_status()
                data = response.json()

                if not data.get('keyOsDetails', {}).get('video_token'):
                    logger.error(f"API response missing video_token: {data}")
                    raise ValueError("M3U8 URL not found in API response")

                m3u8_url = data['keyOsDetails']['video_token']
                logger.info(f"Got M3U8 URL: {m3u8_url[:100]}...")

            # Step 4: Extract cookie from M3U8 response headers
            async with httpx.AsyncClient(
                follow_redirects=False,  # Don't follow redirects to capture Set-Cookie headers
                timeout=30.0,
                headers={"User-Agent": user_agent}
            ) as client:
                response = await client.get(m3u8_url)

                logger.debug(f"M3U8 response status: {response.status_code}")
                logger.debug(f"M3U8 body (first 500 chars): {response.text[:500]}")

                # Extract hdntl from M3U8 body content (matching PHP behavior)
                # Note: The Set-Cookie header contains "hdntl=expired" which is a dummy value
                # The real cookie is embedded in the M3U8 playlist URLs
                # Cookie format: hdntl=exp=...~acl=...~data=...,non-ssai_...~hmac=...
                # Match until whitespace or newline (cookies contain commas in the data field)
                content = response.text
                match = re.search(r'hdntl=([^\s]+)', content)
                if match:
                    cookie = f"hdntl={match.group(1)}"
                    logger.info(f"✓ Generated cookie for channel {channel_id}")
                    logger.info(f"Cookie: {cookie[:150]}...")
                    return cookie

                raise ValueError(f"hdntl cookie not found in M3U8 body. Response (first 500 chars): {content[:500]}")

        except Exception as e:
            logger.error(f"Failed to generate cookie for channel {channel_id}: {e}")
            raise

    async def _get_cached_platform_token(self) -> str:
        """Get platform token with caching (1 hour TTL)"""
        cache_key = "platform_token"
        cached_token = await cache.get(cache_key)

        if cached_token:
            logger.debug("Using cached platform token")
            return cached_token.decode() if isinstance(cached_token, bytes) else cached_token

        # Generate new platform token
        logger.info("Fetching fresh platform token...")
        platform_token = await playwright_service.get_platform_token()

        # Cache for 1 hour
        await cache.set(cache_key, platform_token, ttl=3600)

        return platform_token


# Global instance
channel_cookie_service = ChannelCookieService()
