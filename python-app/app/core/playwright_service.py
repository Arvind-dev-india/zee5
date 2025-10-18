"""
Playwright service for browser automation
Used to extract platform tokens and cookies from ZEE5 website
"""
from typing import Optional, Dict
import asyncio
from playwright.async_api import async_playwright, Browser, Page, Playwright

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("playwright")


class PlaywrightService:
    """Playwright browser automation service"""

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Start Playwright and browser"""
        if self.browser:
            logger.warning("Browser already started")
            return

        try:
            logger.info("Starting Playwright...")
            self.playwright = await async_playwright().start()

            logger.info("Launching Chromium browser...")
            self.browser = await self.playwright.chromium.launch(
                headless=settings.PLAYWRIGHT_HEADLESS,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                ]
            )
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise

    async def stop(self) -> None:
        """Stop browser and Playwright"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            logger.info("Browser closed")

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            logger.info("Playwright stopped")

    async def get_platform_token(self, url: str = None) -> str:
        """
        Extract platform token from ZEE5 website

        Args:
            url: ZEE5 page URL (default: Aaj Tak live TV)

        Returns:
            Platform token string

        Raises:
            ValueError: If token cannot be extracted
        """
        if not self.browser:
            await self.start()

        if not url:
            url = f"{settings.ZEE5_BASE_URL}/live-tv/aaj-tak/0-9-aajtak"

        async with self._lock:
            context = None
            page = None
            try:
                logger.info(f"Fetching platform token from {url}")

                # Create new context with realistic settings
                context = await self.browser.new_context(
                    user_agent=settings.DEFAULT_USER_AGENT,
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-IN',
                    timezone_id='Asia/Kolkata'
                )

                page = await context.new_page()

                # Navigate to page
                response = await page.goto(url, wait_until='domcontentloaded', timeout=settings.PLAYWRIGHT_TIMEOUT)

                if not response or response.status != 200:
                    raise ValueError(f"Failed to load page, status: {response.status if response else 'None'}")

                # Extract platform token from page content
                content = await page.content()

                # Try multiple extraction methods
                token = await self._extract_token_from_content(content, page)

                if not token:
                    raise ValueError("Platform token not found in page")

                logger.info(f"Successfully extracted platform token (length: {len(token)})")
                return token

            except Exception as e:
                logger.error(f"Error extracting platform token: {e}")
                raise ValueError(f"Failed to extract platform token: {e}")

            finally:
                if page:
                    await page.close()
                if context:
                    await context.close()

    async def _extract_token_from_content(self, content: str, page: Page) -> Optional[str]:
        """
        Extract token using multiple methods

        Args:
            content: Page HTML content
            page: Playwright page object

        Returns:
            Platform token or None
        """
        import re

        # Method 1: Regex from HTML
        match = re.search(r'"gwapiPlatformToken"\s*:\s*"([^"]+)"', content)
        if match:
            logger.debug("Token found using regex")
            return match.group(1)

        # Method 2: Try to extract from window object
        try:
            token = await page.evaluate("""
                () => {
                    if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.gwapiPlatformToken) {
                        return window.__INITIAL_STATE__.gwapiPlatformToken;
                    }
                    return null;
                }
            """)
            if token:
                logger.debug("Token found using JavaScript evaluation")
                return token
        except Exception as e:
            logger.debug(f"Could not extract token via JavaScript: {e}")

        # Method 3: Search in all script tags
        try:
            scripts = await page.query_selector_all('script')
            for script in scripts:
                script_content = await script.text_content()
                if script_content and 'gwapiPlatformToken' in script_content:
                    match = re.search(r'"gwapiPlatformToken"\s*:\s*"([^"]+)"', script_content)
                    if match:
                        logger.debug("Token found in script tag")
                        return match.group(1)
        except Exception as e:
            logger.debug(f"Error searching script tags: {e}")

        return None

    async def get_cookie_from_m3u8(self, m3u8_url: str, user_agent: str) -> str:
        """
        Fetch M3U8 URL and extract hdntl cookie

        Args:
            m3u8_url: M3U8 playlist URL
            user_agent: User agent to use

        Returns:
            Cookie string (hdntl=...)

        Raises:
            ValueError: If cookie cannot be extracted
        """
        if not self.browser:
            await self.start()

        async with self._lock:
            context = None
            page = None
            try:
                logger.info("Fetching M3U8 to extract cookie")

                context = await self.browser.new_context(user_agent=user_agent)
                page = await context.new_page()

                # Navigate to M3U8 URL
                response = await page.goto(m3u8_url, timeout=settings.PLAYWRIGHT_TIMEOUT)

                if not response or response.status != 200:
                    raise ValueError(f"Failed to fetch M3U8, status: {response.status if response else 'None'}")

                # Get response body
                content = await page.content()

                # Extract cookie using regex
                import re
                match = re.search(r'hdntl=([^,\s&]+)', content)
                if match:
                    cookie = f"hdntl={match.group(1)}"
                    logger.info(f"Successfully extracted cookie (length: {len(cookie)})")
                    return cookie

                raise ValueError("hdntl cookie not found in M3U8 content")

            except Exception as e:
                logger.error(f"Error extracting cookie from M3U8: {e}")
                raise ValueError(f"Failed to extract cookie: {e}")

            finally:
                if page:
                    await page.close()
                if context:
                    await context.close()


# Global Playwright service instance
playwright_service = PlaywrightService()
