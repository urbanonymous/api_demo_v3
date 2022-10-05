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
            try:
                await websocket.close()
            except Exception:
                pass
            self.active_connections.remove(websocket)

    async def send_data(self, websocket: WebSocket, data: dict):
        if not isinstance(data, dict):
            raise TypeError("data must be a dict")

        await websocket.send_json(data=data)
        logger.info(f"Sent data to client >>> {data}")

    async def broadcast(self, data: dict):
        logger.debug(f"Broadcasting data to clients: {data}")
        for connection in self.active_connections:
            try:
                await self.send_data(connection, data)
            except RuntimeError:
                await self.disconnect(connection)
            except Exception as e:
                logger.exception(e)

    @asynccontextmanager
    async def add_connection(self, websocket: WebSocket):
        try:
            self.active_connections.append(websocket)
            yield websocket
        finally:
            await self.disconnect(websocket)


@lru_cache(maxsize=1)
def get_ws_manager() -> WSManager:
    return WSManager()
