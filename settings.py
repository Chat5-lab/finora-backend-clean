from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./finora.db"
    SECRET_KEY: str = "dev-secret-change-in-production"
    ENV: str = "dev"
    ACCESS_TOKEN_EXPIRE_MIN: int = 30
    REFRESH_TOKEN_EXPIRE_MIN: int = 43200

    # Pydantic v2 style config (replaces inner Config class)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Warn if using default values in production
        if self.ENV == "production" and self.SECRET_KEY == "dev-secret-change-in-production":
            raise ValueError("SECRET_KEY must be set to a secure value in production!")

settings = Settings()
