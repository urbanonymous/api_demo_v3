import os.path
from functools import lru_cache

from fastapi import FastAPI

from src.routers import health_router, templates_router
from src.settings import get_settings

settings = get_settings()


with open(os.path.join(os.path.dirname(__file__), "../VERSION")) as f:
    VERSION = f.read().strip("\n")


class App(FastAPI):
    async def startup(self):
        pass

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
    return app
