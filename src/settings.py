import functools

from pydantic import BaseSettings


class Settings(BaseSettings):
    host: str
    port: int

    liquidity_orders_spread: int = 100
    testnet_api_key: str = "<key>"
    testnet_secret_key: str = "<secret>"


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
