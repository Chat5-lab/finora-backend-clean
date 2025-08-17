from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./finora.db"
    SECRET_KEY: str = "dev-secret"
    ENV: str = "dev"

    class Config:
        env_file = ".env"

settings = Settings()
