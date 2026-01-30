"""
Application Configuration Settings
Uses pydantic-settings for environment variable management
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # MongoDB
    mongodb_uri: str
    database_name: str = "megaartsstore"
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Cloudinary
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    
    # Razorpay (Payment)
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    
    # SMTP (Email)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@megaartsstore.com"
    
    # Blender (Optional)
    blender_enabled: bool = False
    blender_path: str = ""
    
    # Server
    debug: bool = False
    allowed_origins: str = "http://localhost:3000"
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 2000
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse allowed origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def smtp_enabled(self) -> bool:
        """Check if SMTP is configured"""
        return bool(self.smtp_host and self.smtp_user)
    
    @property
    def payment_enabled(self) -> bool:
        """Check if Razorpay is configured"""
        return bool(self.razorpay_key_id and self.razorpay_key_secret)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Convenience export for direct import
settings = get_settings()
