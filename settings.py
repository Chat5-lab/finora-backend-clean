from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./finora.db"
    SECRET_KEY: str = "dev-secret"
    ENV: str = "dev"
    ACCESS_TOKEN_EXPIRE_MIN: int = 30
    REFRESH_TOKEN_EXPIRE_MIN: int = 43200

    # Pydantic v2 style config (replaces inner Config class)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
