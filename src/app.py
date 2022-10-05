import asyncio
import logging
import os
import os.path
from functools import lru_cache

from fastapi import FastAPI

from src.routers import binance_router, health_router
from src.settings import get_settings
from src.utils.binance_liquidity_engine import get_binance_liquidity_engine
from src.utils.binance_ws_client import get_binance_ws_client

logger = logging.getLogger(__name__)

settings = get_settings()
binance_ws_client = get_binance_ws_client()
liquidity_engine = get_binance_liquidity_engine()

with open(os.path.join(os.path.dirname(__file__), "../VERSION")) as f:
    VERSION = f.read().strip("\n")


class App(FastAPI):
    async def startup(self):
        asyncio.ensure_future(binance_ws_client.listen())
        await liquidity_engine.async_init(binance_ws_client)
        asyncio.ensure_future(liquidity_engine.start())

    async def shutdown(self):
        logger.info("Shutting down")
        await liquidity_engine.stop()
        await binance_ws_client.stop()
        os._exit(1)

    async def __aenter__(self):
        await self.startup()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()


@lru_cache
def get_app() -> App:
    app = App(title="API Demo v3", version=VERSION)
    app.include_router(health_router)
    app.include_router(binance_router)
    return app
