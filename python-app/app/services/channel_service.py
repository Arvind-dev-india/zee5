"""
Channel service for loading and managing channel data
"""
import json
from typing import List, Optional
from pathlib import Path

from app.models import Channel, ChannelList
from app.utils.logger import get_logger

logger = get_logger("channel_service")


class ChannelService:
    """Service for managing channel data"""

    def __init__(self, data_file: str = "data/channels.json"):
        self.data_file = Path(data_file)
        self.channels: List[Channel] = []
        self.channel_dict = {}
        self._loaded = False

    async def load_channels(self) -> None:
        """Load channels from JSON file"""
        if self._loaded:
            return

        try:
            if not self.data_file.exists():
                raise FileNotFoundError(f"Channel data file not found: {self.data_file}")

            logger.info(f"Loading channels from {self.data_file}")

            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            channel_list = ChannelList(**data)
            self.channels = channel_list.data

            # Create lookup dictionary
            self.channel_dict = {channel.id: channel for channel in self.channels}

            self._loaded = True
            logger.info(f"Loaded {len(self.channels)} channels")

        except Exception as e:
            logger.error(f"Error loading channels: {e}")
            raise

    def get_channel_by_id(self, channel_id: str) -> Optional[Channel]:
        """Get channel by ID"""
        return self.channel_dict.get(channel_id)

    def get_all_channels(self) -> List[Channel]:
        """Get all channels"""
        return self.channels

    def search_channels(
        self,
        query: str = "",
        genre: Optional[str] = None,
        language: Optional[str] = None,
        country: Optional[str] = None
    ) -> List[Channel]:
        """
        Search channels with filters

        Args:
            query: Search query (matches name, genre, language, id)
            genre: Filter by genre
            language: Filter by language
            country: Filter by country

        Returns:
            List of matching channels
        """
        results = self.channels

        if query:
            query_lower = query.lower()
            results = [
                c for c in results
                if query_lower in c.name.lower()
                or query_lower in c.genre.lower()
                or query_lower in c.language.lower()
                or query_lower in c.id.lower()
            ]

        if genre:
            results = [c for c in results if c.genre.lower() == genre.lower()]

        if language:
            results = [c for c in results if c.language.lower() == language.lower()]

        if country:
            results = [c for c in results if c.country.upper() == country.upper()]

        return results

    def get_genres(self) -> List[str]:
        """Get list of all unique genres"""
        return sorted(set(c.genre for c in self.channels))

    def get_languages(self) -> List[str]:
        """Get list of all unique languages"""
        return sorted(set(c.language for c in self.channels))

    def get_countries(self) -> List[str]:
        """Get list of all unique countries"""
        return sorted(set(c.country for c in self.channels))


# Global channel service instance
channel_service = ChannelService()
