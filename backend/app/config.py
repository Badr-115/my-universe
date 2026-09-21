from functools import lru_cache
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]

class Settings:
    app_name: str = os.getenv("APP_NAME", "Dream Atlas API")
    app_version: str = os.getenv("APP_VERSION", "1.1.0")
    environment: str = os.getenv("ENVIRONMENT", "development").lower()
    cors_origins: list[str] = _csv(os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost"))
    max_dream_length: int = int(os.getenv("MAX_DREAM_LENGTH", "12000"))
    catalog_path: str = str(BASE_DIR / "data" / "city_templates.json")
    lexicon_path: str = str(BASE_DIR / "data" / "lexicon.json")

@lru_cache
def get_settings() -> Settings:
    return Settings()
