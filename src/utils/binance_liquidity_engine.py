import asyncio
import logging
import time
from functools import lru_cache

from src.handlers.binance import cancel_orders, create_order
from src.models.order import Order
from src.models.symbol import SymbolId
from src.settings import get_settings
from src.utils.ws_manager import get_ws_manager

BINANCE_WS_API_URL = "wss://stream.binance.com:9443/ws"

logger = logging.getLogger(__name__)

settings = get_settings()
ws_manager = get_ws_manager()


class BinanceLiquidityEngine(object):
    SYMBOLS_ORDER_SIZE: dict = {"BTCBUSD": {"BUY": 0.01, "SELL": 0.01}, "BTCUSDT": {"BUY": 0.01, "SELL": 0.01}}
    SPREAD: int = settings.liquidity_orders_spread
    TICKS_PER_SECOND: int = settings.liquidity_max_ticks_per_second

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
        """Update symbol price in the class"""
        symbol = data["symbol_id"]
        if symbol not in self._symbols.keys():
            return

        if not self._symbols.get(symbol):
            self._symbols[symbol] = {"orders": [], "price": float(data["price"]), "enabled": False}
        else:
            self._symbols[symbol]["price"] = data["price"]
        logging.debug(f"Updated {symbol} price in BinanceLiquidityEngine")

    async def start(self):
        self._running = True
        while self._running:
            symbols = {**self._symbols}  # Copy dict as it might get updated
            for symbol_id, symbol_data in symbols.items():
                if not symbol_data["enabled"]:
                    continue

                for order in symbol_data["orders"]:
                    conditions = (
                        order["side"] == "BUY" and float(symbol_data["price"]) <= order["price"],
                        order["side"] == "SELL" and float(symbol_data["price"]) >= order["price"],
                    )
                    if any(conditions):
                        try:
                            await self._regenerate_liquidity(symbol_id)
                            break  # Ignore the rest of the orders of the symbol
                        except Exception:
                            logger.error(f"Error generating liquidity for {symbol_id}")

                if not symbol_data["orders"]:
                    try:
                        await self._regenerate_liquidity(symbol_id)
                        break
                    except Exception:
                        logger.error(f"Error generating liquidity for {symbol_id}")
                    continue

            await self._update_clients()
            await asyncio.sleep(1 / self.TICKS_PER_SECOND)  # MAX 2 ticks/s
            logger.debug(f"Tick {time.time()}")

    async def _check_price(self, symbol_id: SymbolId):
        while not self._symbols[symbol_id]["price"]:
            await asyncio.sleep(0.2)

    async def _regenerate_liquidity(self, symbol_id: SymbolId):
        logger.info(f"Recreating orders to provide liquidity for {symbol_id}")
        self._symbols[symbol_id]["orders"] = []
        try:
            await cancel_orders(symbol_id)
        except Exception:
            logger.warning("Couldn't cancel orders")

        if not self._symbols[symbol_id]["price"]:
            await asyncio.wait_for(self._check_price(symbol_id), timeout=5)

        for side in ["BUY", "SELL"]:
            side_modifier = -1 if side == "BUY" else 1
            price = float(self._symbols[symbol_id]["price"]) + (settings.liquidity_orders_spread / 2 * side_modifier)
            order = await create_order(
                {
                    "symbol": symbol_id.upper(),
                    "side": side,
                    "type": "LIMIT",
                    "price": price,
                    "quantity": self.SYMBOLS_ORDER_SIZE[symbol_id][side],
                    "timeInForce": "GTC",
                }
            )
            # Validate order data with Order pydantic model and transform it back to dict
            self._symbols[symbol_id]["orders"].append(dict(Order(**order)))
            asyncio.ensure_future(
                ws_manager.broadcast(
                    {
                        "event_type": "new_order",
                        "symbol_id": symbol_id,
                        "side": side,
                        "size": self.SYMBOLS_ORDER_SIZE[symbol_id][side],
                        "price": price,
                    }
                )
            )

        logger.info(f"Liquidity provided for {symbol_id}")

    async def _update_clients(self):
        events = []
        symbols = {**self._symbols}
        orders = []
        for symbol_id, symbol_data in symbols.items():
            # Add ticker event
            events.append(
                {
                    "event_type": "ticker",
                    "symbol_id": symbol_id,
                    "price": symbol_data["price"],
                }
            )
            # Add orders data, transforming pydantic model to dict
            orders += symbol_data["orders"]

        # Add orders events
        if orders:
            events.append(
                {
                    "event_type": "orders",
                    "orders": orders,
                }
            )
        # TODO: group events and consume them in order at the frontend
        for event in events:
            asyncio.ensure_future(ws_manager.broadcast(event))

    async def stop(self):
        self._running = False
        symbols = [_ for _ in self._symbols.keys()]
        for symbol_id in symbols:
            try:
                await cancel_orders(symbol_id)
            except Exception:
                logger.warning("Couldn't cancel orders")
        logging.info("BinanceLiquidityEngine stopped")


@lru_cache(maxsize=1)
def get_binance_liquidity_engine() -> BinanceLiquidityEngine:
    return BinanceLiquidityEngine()
