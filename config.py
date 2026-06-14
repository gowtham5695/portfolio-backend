from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017/portfolio"
    JWT_SECRET: str = "supersecretjwtkeychangeinproduction123456"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    PORTFOLIO_ADMIN_USERNAME: str = "admin"
    PORTFOLIO_ADMIN_PASSWORD: str = "admin123"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()