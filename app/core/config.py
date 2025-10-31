from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    API_KEY: str = "your_default_api_key"

    class Config:
        env_file = ".env"


settings = Settings()
