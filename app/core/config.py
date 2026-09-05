import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str
    log_level: str
    default_page_size: int
    max_page_size: int


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.environ.get("APP_NAME", "users-service"),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
        default_page_size=int(os.environ.get("DEFAULT_PAGE_SIZE", "50")),
        max_page_size=int(os.environ.get("MAX_PAGE_SIZE", "200")),
    )
