import asyncio
import logging
from functools import lru_cache

from src.handlers.binance import cancel_orders, create_order
from src.models.order import Order
from src.models.symbol import SymbolId
from src.settings import get_settings

BINANCE_WS_API_URL = "wss://stream.binance.com:9443/ws"


logger = logging.getLogger(__name__)
settings = get_settings()


class BinanceLiquidityEngine(object):
    VALID_SYMBOLS: list[str] = ["btcbusd", "btcusdt"]
    SYMBOLS_ORDER_SIZE: dict = {"btcbusd": {"BUY": 0.01, "SELL": 100}, "btcusdt": {"BUY": 0.01, "SELL": 100}}
    SPREAD: int = settings.liquidity_orders_spread

    def __init__(self):
        self._client = None
        self._symbols: dict = {}  # dict with last price and orders, {"BTCBUSD": {"orders":[<order>,], "price":<price>}
        self._running: bool = False

    async def async_init(self, client):
        self._client = client

    async def attach(self, symbol_id: SymbolId):
        if not self._symbols.get(symbol_id):
            self._symbols[symbol_id] = {"orders": [], "price": None, "enabled": True}
        else:
            self._symbols[symbol_id]["enabled"] = True

        await self._client.subscribe(f"{symbol_id.lower()}@miniTicker")
        logger.info("Starting to provide liquidity for {symbol_id}")

    async def detach(self, symbol_id: SymbolId):
        await self._client.unsubscribe(f"{symbol_id}@miniTicker")
        if self._symbols.get(symbol_id):
            self._symbols[symbol_id]["enabled"] = False
        logger.info("Stopped to provide liquidity for {symbol_id}")

    async def update_symbol(self, data: dict):
        symbol = data["symbol_id"]
        if symbol not in self._symbols.keys():
            return

        if not self._symbols.get(symbol):
            self._symbols[symbol] = {"orders": [], "price": data["price"], "enabled": False}
        else:
            self._symbols[symbol]["price"] = data["price"]
        logging.info(f"Updated {symbol} price in BinanceLiquidityEngine")

    async def start(self):
        self._running = True
        while self._running:
            for symbol_id, symbol_data in self._symbols.items():
                if not symbol_data["enabled"]:
                    continue
                for order in symbol_data["orders"]:
                    conditions = (
                        order["side"] == "BUY" and order["price"] >= symbol_data["price"],
                        order["side"] == "SELL" and order["price"] <= symbol_data["price"],
                    )
                    if any(conditions):
                        await self._regenerate_liquidity(symbol_id)
                        break  # Ignore the rest of the orders of the symbol

            await asyncio.sleep(0.5)  # 2 ticks/s

    async def _regenerate_liquidity(self, symbol_id):
        logger.info(f"Recreating orders to provide liquidity for {symbol_id}")
        self._symbols[symbol_id]["orders"] = []
        try:
            await cancel_orders(symbol_id)
        except Exception:
            logger.warning("Couldn't cancel orders")

        await create_order(
            {
                "symbol": symbol_id.upper(),
                "side": "BUY",
                "type": "LIMIT",
                "price": float(self._symbols[symbol_id]["price"]) - settings.liquidity_orders_spread / 2,
                "quantity": self.SYMBOLS_ORDER_SIZE[symbol_id]["BUY"],
                "timeInForce": "GTC",
            }
        )

        await create_order(
            {
                "symbol": symbol_id.upper(),
                "side": "SELL",
                "type": "LIMIT",
                "price": float(self._symbols[symbol_id]["price"]) + settings.liquidity_orders_spread / 2,
                "quantity": self.SYMBOLS_ORDER_SIZE[symbol_id]["SELL"],
                "timeInForce": "GTC",
            }
        )

    async def stop(self):
        self._running = False
        for symbol_id in self._symbols.keys():
            try:
                await cancel_orders(symbol_id)
            except Exception:
                logger.warning("Couldn't cancel orders")
        logging.info("BinanceLiquidityEngine stopped")


@lru_cache(maxsize=1)
def get_binance_liquidity_engine() -> BinanceLiquidityEngine:
    return BinanceLiquidityEngine()
