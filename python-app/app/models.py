"""
Pydantic models for data validation and serialization
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class Channel(BaseModel):
    """Channel model"""
    id: str = Field(..., description="Channel ID")
    slug: str = Field(..., description="Channel slug")
    name: str = Field(..., description="Channel name")
    country: str = Field(..., description="Country code")
    chno: str = Field(..., description="Channel number")
    language: str = Field(..., description="Language code")
    logo: HttpUrl = Field(..., description="Channel logo URL")
    genre: str = Field(..., description="Channel genre")
    url: HttpUrl = Field(..., description="M3U8 stream URL")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "0-9-zeetv",
                "slug": "zee-tv-hd",
                "name": "Zee TV HD",
                "country": "IN",
                "chno": "001",
                "language": "hi",
                "logo": "https://example.com/logo.jpg",
                "genre": "Entertainment",
                "url": "https://example.com/stream.m3u8"
            }
        }


class ChannelList(BaseModel):
    """Channel list response"""
    title: str
    developers: str
    data: List[Channel]


class Cookie(BaseModel):
    """Cookie model"""
    value: str = Field(..., description="Cookie value")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    is_valid: bool = Field(default=True, description="Is cookie valid")
    user_agent: str = Field(..., description="User agent used")
    failure_count: int = Field(default=0, description="Number of failures")

    def is_expired(self) -> bool:
        """Check if cookie is expired"""
        return datetime.now() >= self.expires_at

    def remaining_seconds(self) -> int:
        """Get remaining seconds until expiration"""
        delta = self.expires_at - datetime.now()
        return max(0, int(delta.total_seconds()))


class CookiePoolStatus(BaseModel):
    """Cookie pool status"""
    total_cookies: int
    valid_cookies: int
    expired_cookies: int
    cookies: List[Dict[str, Any]]
    last_refresh: Optional[datetime]
    next_refresh: Optional[datetime]


class StreamRequest(BaseModel):
    """Stream request model"""
    channel_id: str = Field(..., description="Channel ID")
    user_agent: Optional[str] = Field(default=None, description="User agent")


class StreamResponse(BaseModel):
    """Stream response model"""
    success: bool
    channel: Optional[Channel] = None
    stream_url: Optional[str] = None
    cached: bool = False
    expires_in: int = 0
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str]
    cookie_pool: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class TokenPayload(BaseModel):
    """JWT token payload for ZEE5"""
    schema_version: str = "1"
    os_name: str = "N/A"
    os_version: str = "N/A"
    platform_name: str = "Chrome"
    platform_version: str = "104"
    device_name: str = ""
    app_name: str = "Web"
    app_version: str = "2.52.31"
    player_capabilities: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "audio_channel": ["STEREO"],
            "video_codec": ["H264"],
            "container": ["MP4", "TS"],
            "package": ["DASH", "HLS"],
            "resolution": ["240p", "SD", "HD", "FHD"],
            "dynamic_range": ["SDR"]
        }
    )
    security_capabilities: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "encryption": ["WIDEVINE_AES_CTR"],
            "widevine_security_level": ["L3"],
            "hdcp_version": ["HDCP_V1", "HDCP_V2", "HDCP_V2_1", "HDCP_V2_2"]
        }
    )


class ZEE5APIRequest(BaseModel):
    """ZEE5 API request model"""
    channel_id: str
    device_id: str
    platform_name: str = "desktop_web"
    translation: str = "en"
    user_language: str = "en,hi"
    country: str = "IN"
    state: str = ""
    app_version: str = "4.24.0"
    user_type: str = "guest"
    check_parental_control: bool = False


class ZEE5APIResponse(BaseModel):
    """ZEE5 API response model"""
    keyOsDetails: Optional[Dict[str, Any]] = None
    assetDetails: Optional[Dict[str, Any]] = None
