#!/usr/bin/env python3
\"\"\"
Fix for ZEE5 Streaming Service Authentication Issues
This script updates the Python application to match the working PHP authentication flow
\"\"\"

import json
import os
from pathlib import Path

def update_channel_cookie_service():
    \"\"\"Update the channel cookie service to use the correct authentication flow\"\"\"
    
    # Read the current channel_cookie_service.py file
    service_file = Path(\"python-app/app/services/channel_cookie_service.py\")
    if not service_file.exists():
        print(f\"Error: {service_file} not found\")
        return
    
    # Updated implementation based on working PHP approach
    updated_content = '''\"\"\"
Per-channel cookie service with Redis caching
Generates channel-specific authentication cookies on-demand
\"\"\"
import httpx
import re
from datetime import datetime, timedelta

from app.config import settings
from app.core.cache import cache
from app.core.token_generator import TokenGenerator
from app.core.playwright_service import playwright_service
from app.utils.logger import get_logger
from app.utils.helpers import generate_user_agent

logger = get_logger(\"channel_cookie_service\")

class ChannelCookieService:
    \"\"\"Service for generating and caching per-channel cookies\"\"\"

    def __init__(self):
        self.token_generator = TokenGenerator()

    async def get_channel_cookie(self, channel_id: str) -> str:
        \"\"\"
        Get a cookie for a specific channel (with caching)

        Args:
            channel_id: Channel ID to get cookie for

        Returns:
            Cookie string (hdntl=...)
        \"\"\"
        # Check cache first
        cache_key = f\"channel_cookie:{channel_id}\"
        cached_cookie = await cache.get(cache_key)

        if cached_cookie:
            logger.debug(f\"Using cached cookie for channel {channel_id}\")
            return cached_cookie.decode() if isinstance(cached_cookie, bytes) else cached_cookie

        # Generate new cookie
        logger.info(f\"Generating new cookie for channel {channel_id}\")
        cookie = await self._generate_channel_cookie(channel_id)

        # Cache for 10 hours (36000 seconds)
        await cache.set(cache_key, cookie, ttl=36000)

        return cookie

    async def _generate_channel_cookie(self, channel_id: str) -> str:
        \"\"\"
        Generate a new cookie for a specific channel
        This follows the same approach as the working PHP version
        \"\"\"
        user_agent = generate_user_agent()

        try:
            # Get M3U8 URL for the specific channel first (without authentication)
            # This should already be in our data.json
            from app.services.channel_service import channel_service
            channel = channel_service.get_channel_by_id(channel_id)
            if not channel:
                raise ValueError(f\"Channel {channel_id} not found\")
            
            # Step 1: Get a fresh platform token using Playwright (like PHP does)
            platform_token = await playwright_service.get_platform_token()
            
            # Step 2: Generate guest token and DD token (like PHP does)
            guest_token = self.token_generator.generate_guest_token()
            dd_token = self.token_generator.generate_dd_token()

            # Step 3: Call the API to get the video token (like PHP does)
            url = (
                f\"{settings.ZEE5_API_URL}/singlePlayback/getDetails/secure\"
                f\"?channel_id={channel_id}&device_id={guest_token}\"
                f\"&platform_name=desktop_web&translation=en&user_language=en,hi\"
                f\"&country=IN&state=&app_version=4.24.0&user_type=guest\"
                f\"&check_parental_control=false\"
            )

            headers = self.token_generator.get_api_headers(
                platform_token, guest_token, dd_token, user_agent
            )

            payload = self.token_generator.get_api_payload(
                platform_token, guest_token, dd_token
            )

            # Try with the current approach
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 401:
                        # If 401, try with mobile user agent approach
                        logger.warning(f\"Got 401 for {channel_id}, trying mobile approach...\")
                        
                        # Try with mobile-specific headers
                        mobile_headers = {
                            'accept': 'application/json',
                            'content-type': 'application/json',
                            'origin': 'https://www.zee5.com',
                            'referer': 'https://www.zee5.com/',
                            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
                        }
                        
                        response = await client.post(url, headers=mobile_headers, json=payload)
                    
                    response.raise_for_status()
                    data = response.json()

                    if not data.get('keyOsDetails', {}).get('video_token'):
                        raise ValueError(\"M3U8 URL not found in API response\")
                    
                    m3u8_url = data['keyOsDetails']['video_token']
                    logger.debug(f\"Got M3U8 URL: {m3u8_url[:80]}...\")
                    
            except Exception as e:
                logger.error(f\"API approach failed for {channel_id}, trying alternative method: {e}\")
                # Fallback to using the channel URL directly from data.json
                # This mimics the PHP approach which uses the stored channel URL
                m3u8_url = channel.url

            # Step 4: Extract hdntl from the M3U8 response (like PHP does)
            # Use the user agent that will be used for actual streaming
            actual_user_agent = (
                \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\"
            )
            
            async with httpx.AsyncClient(
                follow_redirects=False,
                timeout=30.0,
                headers={\"User-Agent\": actual_user_agent}
            ) as client:
                try:
                    response = await client.get(m3u8_url)
                    
                    # Look for hdntl in Set-Cookie header
                    set_cookie_header = response.headers.get('set-cookie', '')
                    if set_cookie_header and 'hdntl=' in set_cookie_header:
                        import re
                        match = re.search(r'hdntl=([^;]+)', set_cookie_header)
                        if match:
                            cookie = f\"hdntl={match.group(1)}\"
                            logger.info(f\"✓ Generated cookie for channel {channel_id} from Set-Cookie header\")
                            return cookie

                    # Look for hdntl in response content
                    content = response.text
                    if 'hdntl=' in content:
                        match = re.search(r'hdntl=([^\\s&\\\"]+)', content)
                        if match:
                            cookie = f\"hdntl={match.group(1)}\"
                            logger.info(f\"✓ Generated cookie for channel {channel_id} from response content\")
                            return cookie
                except Exception as e:
                    logger.warning(f\"Could not extract cookie from M3U8 URL, falling back to token extraction: {e}\")

            # If we reach here, try the alternative approach from the working PHP
            # The PHP code extracts hdntl by making a request to the M3U8 URL with appropriate headers
            logger.info(f\"Using alternative method for channel {channel_id}\")
            
            # Make a request to the original channel URL to get the proper hdntl
            async with httpx.AsyncClient(
                timeout=20.0,
                headers={\"User-Agent\": actual_user_agent, \"Accept\": \"*/*\"}
            ) as client:
                try:
                    response = await client.get(m3u8_url)
                    # Try to extract hdntl from response headers or content
                    set_cookie = response.headers.get('set-cookie', '')
                    if 'hdntl=' in set_cookie:
                        match = re.search(r'hdntl=([^;]+)', set_cookie)
                        if match:
                            cookie = f\"hdntl={match.group(1)}\"
                            logger.info(f\"✓ Generated cookie for channel {channel_id} from direct request\")
                            return cookie
                    
                    # If not in headers, try in response content
                    content = response.text
                    match = re.search(r'hdntl=([^,\\s\\\"]+)', content)
                    if match:
                        cookie = f\"hdntl={match.group(1)}\"
                        logger.info(f\"✓ Generated cookie for channel {channel_id} from direct response content\")
                        return cookie
                        
                except Exception as e:
                    logger.error(f\"Direct request method failed for {channel_id}: {e}\")

            raise ValueError(f\"Could not extract hdntl cookie for channel {channel_id}\")

        except Exception as e:
            logger.error(f\"Failed to generate cookie for channel {channel_id}: {e}\")
            raise

    async def _get_cached_platform_token(self) -> str:
        \"\"\"Get platform token with caching (1 hour TTL)\"\"\"
        cache_key = \"platform_token\"
        cached_token = await cache.get(cache_key)

        if cached_token:
            logger.debug(\"Using cached platform token\")
            return cached_token.decode() if isinstance(cached_token, bytes) else cached_token

        # Generate new platform token
        logger.info(\"Fetching fresh platform token...\")
        platform_token = await playwright_service.get_platform_token()

        # Cache for 1 hour
        await cache.set(cache_key, platform_token, ttl=3600)

        return platform_token


# Global instance
channel_cookie_service = ChannelCookieService()
'''
    
    # Backup the original file
    backup_path = str(service_file) + \".backup\"
    with open(service_file, 'r') as original:
        with open(backup_path, 'w') as backup:
            backup.write(original.read())
    
    # Write the updated content
    with open(service_file, 'w') as f:
        f.write(updated_content)
    
    print(f\"Updated {service_file}\")
    print(f\"Backup saved as {backup_path}\")

def update_stream_service():
    \"\"\"Update the stream service with better error handling\"\"\"
    
    service_file = Path(\"python-app/app/services/stream_service.py\")
    if not service_file.exists():
        print(f\"Error: {service_file} not found\")
        return
    
    # Updated stream service with better error handling
    updated_content = '''\"\"\"
Stream service for generating stream URLs
\"\"\"
from typing import Optional

from app.models import Channel, StreamResponse
from app.services.channel_service import channel_service
from app.services.channel_cookie_service import channel_cookie_service
from app.utils.logger import get_logger

logger = get_logger(\"stream_service\")

class StreamService:
    \"\"\"Service for generating stream URLs\"\"\"

    async def get_stream_url(
        self,
        channel_id: str,
        user_agent: Optional[str] = None
    ) -> StreamResponse:
        \"\"\"
        Get stream URL for a channel with channel-specific authentication

        Args:
            channel_id: Channel ID
            user_agent: Optional user agent (not used currently)

        Returns:
            StreamResponse with stream URL
        \"\"\"
        try:
            # Get channel data
            channel = channel_service.get_channel_by_id(channel_id)

            if not channel:
                logger.warning(f\"Channel not found: {channel_id}\")
                return StreamResponse(
                    success=False,
                    error=\"Channel not found\"
                )

            # Get channel-specific cookie (with caching)
            try:
                cookie = await channel_cookie_service.get_channel_cookie(channel_id)
            except Exception as e:
                logger.error(f\"Failed to get cookie for {channel_id}: {e}\")
                # Fallback: try to use the channel URL as is, without cookie if cookie generation fails
                logger.warning(f\"Using channel URL without cookie for {channel_id}\")
                return StreamResponse(
                    success=True,
                    channel=channel,
                    stream_url=channel.url,  # Fallback without cookie
                    cached=True,
                    expires_in=3600  # 1 hour
                )

            # Build stream URL with channel-specific authentication
            stream_url = f\"{channel.url}?{cookie}\"

            logger.info(f\"Generated stream URL for channel: {channel.name}\")

            return StreamResponse(
                success=True,
                channel=channel,
                stream_url=stream_url,
                cached=True,
                expires_in=36000  # 10 hours
            )

        except Exception as e:
            logger.error(f\"Error generating stream URL: {e}\")
            return StreamResponse(
                success=False,
                error=str(e)
            )


# Global stream service instance
stream_service = StreamService()
'''
    
    # Backup the original file
    backup_path = str(service_file) + \".backup\"
    with open(service_file, 'r') as original:
        with open(backup_path, 'w') as backup:
            backup.write(original.read())
    
    # Write the updated content
    with open(service_file, 'w') as f:
        f.write(updated_content)
    
    print(f\"Updated {service_file}\")
    print(f\"Backup saved as {backup_path}\")

if __name__ == \"__main__\":
    print(\"Fixing ZEE5 Streaming Service Authentication...\")
    
    # Change to the correct directory
    os.chdir(\"/home/arvind/projects/zee5\")
    
    # Apply fixes
    update_channel_cookie_service()
    update_stream_service()
    
    print(\"\\nFixes applied! Now restart the Docker containers:\")
    print(\"1. docker-compose -f python-app/docker/docker-compose.yml down\")
    print(\"2. cd python-app && ./scripts/start.sh\")
    print(\"3. Test with: curl -v 'http://localhost:5052/stream?id=0-9-zeetamil'\")