import logging
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WSManager:
    """The WebSocket Manager is going to broadcast messages to all the ws clients connnected."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_data(self, websocket: WebSocket, data: dict):
        if not isinstance(data, dict):
            raise TypeError("data must be a dict")

        await websocket.send_json(
            data={"data": data},
            mode="text",
        )

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await self.send_data(connection, data)
            except Exception as e:
                logger.exception(e)

    @asynccontextmanager
    async def create_session(self, websocket: WebSocket):
        try:
            self.active_connections.append(websocket)
            yield websocket
        finally:
            await self.disconnect(websocket)


@lru_cache(maxsize=1)
def get_ws_manager() -> WSManager:
    return WSManager()