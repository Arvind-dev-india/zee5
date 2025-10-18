"""
Configuration management using Pydantic Settings
Loads environment variables with validation
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "ZEE5 Streaming Service"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=5052, description="Server port")
    SERVER_URL: Optional[str] = Field(default=None, description="Public server URL")

    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    USE_REDIS: bool = Field(default=True, description="Enable Redis caching")

    # Cache
    CACHE_DIR: str = Field(default="data/cache", description="File cache directory")
    COOKIE_CACHE_TTL: int = Field(default=43000, description="Cookie cache TTL in seconds (12 hours)")

    # Cookie Manager
    COOKIE_POOL_SIZE: int = Field(default=1, description="Number of cookies to maintain in pool")
    COOKIE_REFRESH_INTERVAL: int = Field(default=36000, description="Cookie refresh interval (10 hours)")
    COOKIE_MIN_REMAINING: int = Field(default=3600, description="Minimum remaining time before refresh")

    # Playwright
    PLAYWRIGHT_HEADLESS: bool = Field(default=True, description="Run Playwright in headless mode")
    PLAYWRIGHT_TIMEOUT: int = Field(default=60000, description="Playwright timeout in ms")

    # ZEE5 API
    ZEE5_BASE_URL: str = "https://www.zee5.com"
    ZEE5_API_URL: str = "https://spapi.zee5.com"
    ZEE5_CDN_URL: str = "https://z5ak-cmaflive.zee5.com"

    # User Agents
    DEFAULT_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")
    LOG_JSON: bool = Field(default=False, description="Use JSON logging format")

    # Security
    ALLOWED_ORIGINS: list[str] = Field(default=["*"], description="CORS allowed origins")

    # Feature Flags
    ENABLE_METRICS: bool = Field(default=False, description="Enable Prometheus metrics")
    ENABLE_DEBUG_ROUTES: bool = Field(default=True, description="Enable debug endpoints")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def base_url(self) -> str:
        """Get the base URL for the service"""
        if self.SERVER_URL:
            return self.SERVER_URL
        return f"http://{self.HOST}:{self.PORT}"


# Global settings instance
settings = Settings()
