from pydantic_settings import BaseSettings
from pathlib import Path

# Build an absolute path to the project's root directory
# BASE_DIR is .../test_aplication/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str
    API_KEY: str = "your_default_api_key"

    class Config:
        env_file = BASE_DIR / ".env"


settings = Settings()
