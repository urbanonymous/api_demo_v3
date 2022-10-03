import asyncio
import json
import logging
from functools import lru_cache

import websockets

from src.handlers.binance import cancel_orders
from src.models.binance import SymbolId

logger = logging.getLogger(__name__)

BINANCE_WS_API_URL = "wss://stream.binance.com:9443/ws"


class BinanceLiquidityEngine(object):
    VALID_SYMBOLS: list[str] = ["BTCUSD", "BTCUSDT"]

    def __init__(self):
        self._symbols: dict = {}  # dict with last price and orders, {"BTCUSD": {"orders":[<order>,], "price":<price>}
        self._running: bool = False

    async def attach(self, symbol_id: SymbolId):
        self._symbols.remove(symbol_id)

    async def detach(self, symbol_id: SymbolId):
        self._symbols.remove(symbol_id)

    async def update_symbol(self, data: dict):
        symbol = data["symbol"]
        if symbol not in self._symbols.keys():
            return

        if not self._symbols.get(symbol):
            self._symbols[symbol] = {
                "orders": [],
                "price": data["price"],
            }
        else:
            self._symbols[symbol]["price"] = data["price"]
        logging.info(f"Updated {symbol} price in BinanceLiquidityEngine")

    async def check_connection(self):
        while not self._connection:
            await asyncio.sleep(0.1)

    async def start(self):
        self._running = True
        while self._running:
            await asyncio.sleep(0.2)  # 5 ticks/s

    async def stop(self):
        self._running = False
        for symbol in self._symbols.keys():
            await cancel_orders(symbol)
        logging.info("BinanceLiquidityEngine stopped")


@lru_cache(maxsize=1)
def get_binance_liquidity_engine() -> BinanceLiquidityEngine:
    return BinanceLiquidityEngine()
