import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    youtube_api_key: str
    app_env: str = "development"
    log_level: str = "INFO"
    
    # Notification Settings
    slack_webhook_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Reporting
    report_output_dir: str = "reports"
    
    # Domain Thresholds
    min_engagement_threshold: float = 0.02
    max_upload_gap_days: int = 10
    
    # Database
    db_url: str = "sqlite:///./youtube_toolkit.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
