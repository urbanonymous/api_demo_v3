import asyncio
import json
import logging
from functools import lru_cache

import websockets

logger = logging.getLogger(__name__)

BINANCE_WS_API_URL = "wss://stream.binance.com:9443/ws"


class BinanceWSClient(object):
    def __init__(self):
        self._queue = asyncio.Queue()
        self._connection = None
        self._id = 0

    async def listen(self):
        try:
            async with websockets.connect(BINANCE_WS_API_URL) as connection:
                self._connection = connection
                while connection.open:
                    try:
                        message = await connection.recv()
                        asyncio.create_task(self._handle_message(message))
                    except Exception as e:
                        logger.exception(e)
            logger.warning("BinanceWSClient is not listening anymore")
        except Exception as e:
            logger.exception(e)

    async def subscribe(self, stream: str):
        try:
            self._id += 1
            await self.send(json.dumps({"method": "SUBSCRIBE", "params": [stream], "id": self._id}))
        except Exception as e:
            logger.exception(e)

    async def check_connection(self):
        while not self._connection:
            await asyncio.sleep(0.1)

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


@lru_cache(maxsize=1)
def get_binance_ws_client() -> BinanceWSClient:
    return BinanceWSClient()
