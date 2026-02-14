from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings."""

    DATABASE_URL: str = "sqlite:///./data/stories.db"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    DEFAULT_BACKEND: str = "lmstudio"


settings = Settings()
