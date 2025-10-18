"""
Cookie manager with pool management and automatic refresh
This is the core component that manages ZEE5 authentication cookies
"""
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import httpx

from app.config import settings
from app.models import Cookie, CookiePoolStatus
from app.core.playwright_service import playwright_service
from app.core.token_generator import TokenGenerator
from app.core.cache import cache
from app.utils.logger import get_logger
from app.utils.helpers import generate_user_agent

logger = get_logger("cookie_manager")


class CookieManager:
    """
    Manages cookie pool with automatic generation and refresh
    """

    def __init__(self):
        self.cookies: List[Cookie] = []
        self.token_generator = TokenGenerator()
        self._lock = asyncio.Lock()
        self.last_refresh: Optional[datetime] = None
        self.next_refresh: Optional[datetime] = None

    async def initialize(self) -> None:
        """Initialize cookie pool"""
        logger.info("Initializing cookie manager...")

        # Try to load cached cookies first
        await self._load_cached_cookies()

        # If no valid cookies, generate new ones
        if not self._has_valid_cookie():
            logger.info("No valid cookies found, generating initial pool...")
            await self.refresh_pool()
        else:
            logger.info(f"Loaded {len(self.cookies)} cached cookies")

        # Schedule next refresh
        self._schedule_next_refresh()

    async def get_cookie(self) -> str:
        """
        Get a valid cookie from the pool

        Returns:
            Cookie value string

        Raises:
            ValueError: If no valid cookies available
        """
        async with self._lock:
            # Try to get a valid cookie
            valid_cookies = [c for c in self.cookies if c.is_valid and not c.is_expired()]

            if not valid_cookies:
                logger.warning("No valid cookies in pool, generating new one...")
                try:
                    await self._generate_single_cookie()
                    valid_cookies = [c for c in self.cookies if c.is_valid and not c.is_expired()]
                except Exception as e:
                    logger.error(f"Failed to generate cookie: {e}")
                    raise ValueError("No valid cookies available")

            if not valid_cookies:
                raise ValueError("Failed to get valid cookie")

            # Return the cookie with most remaining time
            best_cookie = max(valid_cookies, key=lambda c: c.remaining_seconds())
            logger.debug(f"Returning cookie with {best_cookie.remaining_seconds()}s remaining")

            return best_cookie.value

    async def refresh_pool(self) -> None:
        """Refresh the entire cookie pool"""
        async with self._lock:
            logger.info(f"Refreshing cookie pool (target size: {settings.COOKIE_POOL_SIZE})")

            new_cookies = []
            for i in range(settings.COOKIE_POOL_SIZE):
                try:
                    logger.info(f"Generating cookie {i + 1}/{settings.COOKIE_POOL_SIZE}")
                    cookie = await self._generate_cookie()
                    new_cookies.append(cookie)

                    # Add small delay between generations
                    if i < settings.COOKIE_POOL_SIZE - 1:
                        await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"Failed to generate cookie {i + 1}: {e}")
                    continue

            if new_cookies:
                self.cookies = new_cookies
                await self._save_cookies_to_cache()
                logger.info(f"Successfully refreshed {len(new_cookies)} cookies")
            else:
                logger.error("Failed to generate any new cookies")

            self.last_refresh = datetime.now()
            self._schedule_next_refresh()

    async def _generate_cookie(self) -> Cookie:
        """
        Generate a new cookie using Playwright

        Returns:
            Cookie object
        """
        # Use fixed user agent matching PHP version
        from app.config import settings
        user_agent = settings.DEFAULT_USER_AGENT

        try:
            # Step 1: Get platform token
            logger.debug("Fetching platform token...")
            platform_token = await playwright_service.get_platform_token()

            # Step 2: Generate guest and DD tokens
            guest_token = self.token_generator.generate_guest_token()
            dd_token = self.token_generator.generate_dd_token()

            # Step 3: Get M3U8 URL from ZEE5 API
            logger.debug("Fetching M3U8 URL from ZEE5 API...")
            m3u8_url = await self._fetch_m3u8_url(
                platform_token, guest_token, dd_token, user_agent
            )

            # Step 4: Extract hdntl cookie from M3U8
            logger.debug("Extracting cookie from M3U8...")
            cookie_value = await self._extract_cookie_from_m3u8(m3u8_url, user_agent)

            # Create Cookie object
            created_at = datetime.now()
            expires_at = created_at + timedelta(seconds=settings.COOKIE_CACHE_TTL)

            cookie = Cookie(
                value=cookie_value,
                created_at=created_at,
                expires_at=expires_at,
                is_valid=True,
                user_agent=user_agent,
                failure_count=0
            )

            logger.info(f"Successfully generated cookie (expires in {cookie.remaining_seconds()}s)")
            return cookie

        except Exception as e:
            logger.error(f"Cookie generation failed: {e}")
            raise

    async def _generate_single_cookie(self) -> None:
        """Generate a single cookie and add to pool"""
        try:
            cookie = await self._generate_cookie()
            self.cookies.append(cookie)
            await self._save_cookies_to_cache()
        except Exception as e:
            logger.error(f"Failed to generate single cookie: {e}")
            raise

    async def _fetch_m3u8_url(
        self,
        platform_token: str,
        guest_token: str,
        dd_token: str,
        user_agent: str
    ) -> str:
        """
        Fetch M3U8 URL from ZEE5 API

        Args:
            platform_token: Platform access token
            guest_token: Guest user token
            dd_token: Device details token
            user_agent: User agent string

        Returns:
            M3U8 URL string
        """
        url = (
            f"{settings.ZEE5_API_URL}/singlePlayback/getDetails/secure"
            f"?channel_id=0-9-aajtak&device_id={guest_token}"
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
            response.raise_for_status()

            data = response.json()

            if not data.get('keyOsDetails', {}).get('video_token'):
                raise ValueError("M3U8 URL not found in API response")

            m3u8_url = data['keyOsDetails']['video_token']
            logger.debug(f"Got M3U8 URL: {m3u8_url[:50]}...")

            return m3u8_url

    async def _extract_cookie_from_m3u8(self, m3u8_url: str, user_agent: str) -> str:
        """
        Extract cookie from M3U8 URL

        Args:
            m3u8_url: M3U8 playlist URL
            user_agent: User agent string

        Returns:
            Cookie value string (hdntl=...)
        """
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": user_agent}
        ) as client:
            response = await client.get(m3u8_url)
            response.raise_for_status()

            content = response.text

            # Extract hdntl cookie using regex
            # Note: Cookie contains commas, so don't stop at commas
            import re
            match = re.search(r'hdntl=([^\s&]+)', content)
            if match:
                return f"hdntl={match.group(1)}"

            raise ValueError("hdntl cookie not found in M3U8 content")

    async def _load_cached_cookies(self) -> None:
        """Load cookies from cache"""
        try:
            import json

            cached_data = await cache.get("cookie_pool")
            if not cached_data:
                return

            data = json.loads(cached_data)
            cookies = []

            for cookie_data in data.get("cookies", []):
                cookie = Cookie(
                    value=cookie_data["value"],
                    created_at=datetime.fromisoformat(cookie_data["created_at"]),
                    expires_at=datetime.fromisoformat(cookie_data["expires_at"]),
                    is_valid=cookie_data["is_valid"],
                    user_agent=cookie_data["user_agent"],
                    failure_count=cookie_data.get("failure_count", 0)
                )

                # Only keep non-expired cookies
                if not cookie.is_expired():
                    cookies.append(cookie)

            if cookies:
                self.cookies = cookies
                logger.info(f"Loaded {len(cookies)} cookies from cache")

        except Exception as e:
            logger.error(f"Error loading cached cookies: {e}")

    async def _save_cookies_to_cache(self) -> None:
        """Save cookies to cache"""
        try:
            import json

            data = {
                "cookies": [
                    {
                        "value": c.value,
                        "created_at": c.created_at.isoformat(),
                        "expires_at": c.expires_at.isoformat(),
                        "is_valid": c.is_valid,
                        "user_agent": c.user_agent,
                        "failure_count": c.failure_count
                    }
                    for c in self.cookies
                ],
                "last_refresh": datetime.now().isoformat()
            }

            await cache.set(
                "cookie_pool",
                json.dumps(data),
                ttl=settings.COOKIE_CACHE_TTL
            )

            logger.debug("Saved cookies to cache")

        except Exception as e:
            logger.error(f"Error saving cookies to cache: {e}")

    def _has_valid_cookie(self) -> bool:
        """Check if pool has at least one valid cookie"""
        return any(c.is_valid and not c.is_expired() for c in self.cookies)

    def _schedule_next_refresh(self) -> None:
        """Schedule next refresh time"""
        self.next_refresh = datetime.now() + timedelta(
            seconds=settings.COOKIE_REFRESH_INTERVAL
        )
        logger.info(f"Next refresh scheduled at: {self.next_refresh}")

    async def should_refresh(self) -> bool:
        """Check if pool should be refreshed"""
        # No valid cookies - refresh immediately
        if not self._has_valid_cookie():
            return True

        # Check if next refresh time has passed
        if self.next_refresh and datetime.now() >= self.next_refresh:
            return True

        # Check if all cookies are close to expiration
        valid_cookies = [c for c in self.cookies if c.is_valid and not c.is_expired()]
        if valid_cookies:
            min_remaining = min(c.remaining_seconds() for c in valid_cookies)
            if min_remaining < settings.COOKIE_MIN_REMAINING:
                logger.info(f"Cookies expiring soon (min remaining: {min_remaining}s)")
                return True

        return False

    def get_status(self) -> CookiePoolStatus:
        """Get cookie pool status"""
        valid_cookies = [c for c in self.cookies if c.is_valid and not c.is_expired()]
        expired_cookies = [c for c in self.cookies if c.is_expired()]

        cookie_details = []
        for i, cookie in enumerate(self.cookies):
            cookie_details.append({
                "index": i,
                "is_valid": cookie.is_valid,
                "is_expired": cookie.is_expired(),
                "remaining_seconds": cookie.remaining_seconds(),
                "created_at": cookie.created_at.isoformat(),
                "expires_at": cookie.expires_at.isoformat(),
                "failure_count": cookie.failure_count
            })

        return CookiePoolStatus(
            total_cookies=len(self.cookies),
            valid_cookies=len(valid_cookies),
            expired_cookies=len(expired_cookies),
            cookies=cookie_details,
            last_refresh=self.last_refresh,
            next_refresh=self.next_refresh
        )


# Global cookie manager instance
cookie_manager = CookieManager()
