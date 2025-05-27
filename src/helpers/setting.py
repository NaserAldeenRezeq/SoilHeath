import os
import json
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str
    APP_VERSION: str
    LOC_DOC: str
    VECTOR_DB: str
    SQLITE_DB: str
    PORT: int
    HOST: str

    # Add these two
    EMBEDDING_MODEL: str
    HUGGINGFACE_TOKIENS: str

    FILE_ALLOWED_TYPES: List[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int

    # Monitoring Settings
    CPU_THRESHOLD: int
    MEMORY_THRESHOLD: int
    MONITOR_INTERVAL: int
    DISK_THRESHOLD: int
    GPUs_THRESHOLD: int

    GPU_AVAILABLE: bool

    # Alert Settings
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    # Secrets
    SECRET_KEY: str

    GOOGLE_API_KEY: str

    @field_validator("FILE_ALLOWED_TYPES", mode="before")
    @classmethod
    def parse_list(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    class Config:
        env_file = os.path.join(root_dir, ".env")
        env_file_encoding = "utf-8"

# Singleton-style getter
from functools import lru_cache

@lru_cache()
def get_settings() -> Settings:
    return Settings()
