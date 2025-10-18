"""
Token generation utilities for ZEE5 API
"""
from typing import Dict, Any

from app.models import TokenPayload
from app.utils.helpers import generate_jwt_token, generate_guest_token
from app.utils.logger import get_logger

logger = get_logger("token_generator")


class TokenGenerator:
    """Generate tokens required for ZEE5 API"""

    @staticmethod
    def generate_dd_token() -> str:
        """
        Generate DD (Device Details) token

        Returns:
            JWT token string
        """
        payload_data = TokenPayload().model_dump()
        token = generate_jwt_token(payload_data)
        logger.debug("Generated DD token")
        return token

    @staticmethod
    def generate_guest_token() -> str:
        """
        Generate guest user token (UUID format)

        Returns:
            Guest token string
        """
        token = generate_guest_token()
        logger.debug(f"Generated guest token: {token}")
        return token

    @staticmethod
    def get_api_headers(
        platform_token: str,
        guest_token: str,
        dd_token: str,
        user_agent: str
    ) -> Dict[str, str]:
        """
        Get headers for ZEE5 API request

        Args:
            platform_token: Platform access token
            guest_token: Guest user token
            dd_token: Device details token
            user_agent: User agent string

        Returns:
            Headers dictionary
        """
        return {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://www.zee5.com",
            "referer": "https://www.zee5.com/",
            "sec-ch-ua": '"Microsoft Edge";v="139", "Chromium";v="139", "Not:A-Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": user_agent
        }

    @staticmethod
    def get_api_payload(
        platform_token: str,
        guest_token: str,
        dd_token: str
    ) -> Dict[str, str]:
        """
        Get payload for ZEE5 API request

        Args:
            platform_token: Platform access token
            guest_token: Guest user token
            dd_token: Device details token

        Returns:
            Payload dictionary
        """
        return {
            "x-access-token": platform_token,
            "X-Z5-Guest-Token": guest_token,
            "x-dd-token": dd_token
        }
