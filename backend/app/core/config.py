import os
import json
from typing import List, Optional, Union
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MeetFlow AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./meetflow.db"

    # Security
    JWT_SECRET_KEY: str = "meetflow-default-secret-key-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # NVIDIA NIM Hosted LLM
    NVIDIA_API_KEY: Optional[str] = None
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = "meta/llama-3.3-70b-instruct"
    NVIDIA_TIMEOUT_SECONDS: int = 90
    NVIDIA_MAX_RETRIES: int = 3

    # Upload & File constraints
    UPLOAD_MAX_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: Union[List[str], str] = ["txt", "pdf", "docx"]

    # URLs & CORS
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_PUBLIC_URL: str = "http://localhost:8000"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]

    def get_allowed_extensions(self) -> List[str]:
        if isinstance(self.ALLOWED_EXTENSIONS, str):
            return [e.strip() for e in self.ALLOWED_EXTENSIONS.split(",") if e.strip()]
        return self.ALLOWED_EXTENSIONS

    def get_cors_origins(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        return self.CORS_ORIGINS

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
