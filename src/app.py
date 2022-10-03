import asyncio
import os.path
from functools import lru_cache

from fastapi import FastAPI

from src.routers import binance_router, health_router, templates_router
from src.settings import get_settings
from src.utils.binance_ws_client import get_binance_ws_client

settings = get_settings()
binance_ws_client = get_binance_ws_client()

with open(os.path.join(os.path.dirname(__file__), "../VERSION")) as f:
    VERSION = f.read().strip("\n")


class App(FastAPI):
    async def startup(self):
        asyncio.create_task(binance_ws_client.listen())
        # await binance_ws_client.subscribe("btcusdt@miniTicker")

    async def shutdown(self):
        pass

    async def __aenter__(self):
        await self.startup()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()


@lru_cache
def get_app() -> App:
    app = App(title="API Demo v3", version=VERSION)
    app.include_router(health_router)
    app.include_router(templates_router)
    app.include_router(binance_router)
    return app
