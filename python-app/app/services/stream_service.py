"""
Stream service for generating stream URLs
"""
from typing import Optional

from app.models import Channel, StreamResponse
from app.services.channel_service import channel_service
from app.services.channel_cookie_service import channel_cookie_service
from app.utils.logger import get_logger

logger = get_logger("stream_service")


class StreamService:
    """Service for generating stream URLs"""

    async def get_stream_url(
        self,
        channel_id: str,
        user_agent: Optional[str] = None
    ) -> StreamResponse:
        """
        Get stream URL for a channel using global cookie pool

        Note: Like PHP version, we use ONE cookie for ALL channels (not channel-specific)

        Args:
            channel_id: Channel ID
            user_agent: Optional user agent (not used currently)

        Returns:
            StreamResponse with stream URL
        """
        try:
            # Get channel data
            channel = channel_service.get_channel_by_id(channel_id)

            if not channel:
                logger.warning(f"Channel not found: {channel_id}")
                return StreamResponse(
                    success=False,
                    error="Channel not found"
                )

            # Get per-channel cookie (each channel needs matching ACL)
            try:
                cookie = await channel_cookie_service.get_channel_cookie(channel_id)
            except Exception as e:
                logger.error(f"Failed to get cookie for {channel_id}: {e}")
                return StreamResponse(
                    success=False,
                    error=f"Cookie generation failed: {str(e)}",
                    channel=channel
                )

            # Build stream URL with authentication
            stream_url = f"{channel.url}?{cookie}"

            logger.info(f"Generated stream URL for channel: {channel.name}")

            return StreamResponse(
                success=True,
                channel=channel,
                stream_url=stream_url,
                cached=True,
                expires_in=36000  # 10 hours
            )

        except Exception as e:
            logger.error(f"Error generating stream URL: {e}")
            return StreamResponse(
                success=False,
                error=str(e)
            )


# Global stream service instance
stream_service = StreamService()
