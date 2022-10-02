import functools

from pydantic import BaseSettings


class Settings(BaseSettings):
    host: str
    port: int


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
