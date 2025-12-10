from functools import lru_cache
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # App
    api_name: str = "VigyapanAI SaaS"
    api_version: str = "0.1.0"
    debug: bool = False
    frontend_url: str = "http://localhost:8080"

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_jwt_secret: str

    # Hosted models
    replicate_api_token: str
    google_api_key: str

    # Storage
    s3_bucket: str
    s3_region: str = "us-east-1"
    s3_endpoint: Optional[str] = None
    s3_access_key_id: str
    s3_secret_access_key: str

    # Redis / queue
    redis_url: str = "redis://redis:6379/0"

    # Billing
    razorpay_key_id: str
    razorpay_key_secret: str

    # Rate limiting
    rate_limit_requests: int = 20
    rate_limit_window_seconds: int = 3600

    # Media defaults
    generation_fps: int = 24
    generation_resolution: str = "1280x720"
    generation_scenes: int = 6
    max_upload_mb: int = 100

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class RateLimitKey(BaseModel):
    user_id: str
    window_seconds: int


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]

