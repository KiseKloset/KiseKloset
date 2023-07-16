from pathlib import Path

from pydantic import BaseSettings

FILE = Path(__file__).resolve()
ROOT = FILE.parent.parent


class Settings(BaseSettings):
    HOST: str
    PORT: int
    CORS_ORIGINS: list[str]
    CORS_HEADERS: list[str]

    class Config:
        env_file = ROOT / '.env'


settings = Settings()
