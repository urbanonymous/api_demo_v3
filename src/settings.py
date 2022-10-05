import functools

from pydantic import BaseSettings


class Settings(BaseSettings):
    host: str
    port: int

    liquidity_orders_spread: int = 100
    liquidity_max_ticks_per_second: int = 2

    testnet_api_key: str
    testnet_secret_key: str


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
