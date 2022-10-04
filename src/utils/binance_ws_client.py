import asyncio
import json
import logging
from functools import lru_cache

import websockets

from src.services.binance import events_map

logger = logging.getLogger(__name__)

BINANCE_WS_API_URL = "wss://stream.binance.com:9443/ws"


class BinanceWSClient(object):
    def __init__(self):
        self._queue = asyncio.Queue()
        self._connection = None
        self._id = 0
        self._running = False

    async def listen(self):
        self._running = True
        try:
            async with websockets.connect(BINANCE_WS_API_URL) as connection:
                self._connection = connection
                while connection.open and self._running:
                    async for message in connection:
                        try:
                            await self._handle_message(message)
                        except Exception as e:
                            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        logger.warning("BinanceWSClient is not listening anymore")

    async def subscribe(self, stream: str):
        try:
            self._id += 1
            await self.send(json.dumps({"method": "SUBSCRIBE", "params": [stream], "id": self._id}))
        except Exception as e:
            logger.exception(e)

    async def unsubscribe(self, stream: str):
        self._id += 1
        await self.send(json.dumps({"method": "UNSUBSCRIBE", "params": [stream], "id": self._id}))


    async def check_connection(self):
        while not self._connection:
            await asyncio.sleep(0.2)

    async def send(self, message: str):
        try:
            if not self._connection:
                await asyncio.wait_for(self.check_connection(), timeout=3)
            await self._connection.send(message)
            logger.info(f">>> {message}")
        except Exception as e:
            logger.exception(e)

    async def _handle_message(self, message: str):
        logger.info(f"<<< {message}")
        try:
            # Ignore non json messages
            event = json.loads(message)
            event_type = event.get("e")
            if event_type in events_map.keys():
                await events_map[event_type](event)
            else:
                logger.info(f"Ignored event {event}")
        except Exception as e:
            logger.exception(e)

    async def stop(self):
        self._runnig = False
        logger.info("Stopping BinanceWSClient")


@lru_cache(maxsize=1)
def get_binance_ws_client() -> BinanceWSClient:
    return BinanceWSClient()
