import logging

from src.models.symbol import SymbolId
from src.utils.binance_liquidity_engine import get_binance_liquidity_engine
from src.utils.ws_manager import get_ws_manager

logger = logging.getLogger(__name__)

ws_manager = get_ws_manager()
liquidity_engine = get_binance_liquidity_engine()


async def enable_symbol_liquidity(symbol_id: SymbolId):
    await liquidity_engine.attach(symbol_id)
    return {"status": "ok", "data": {"symbol_id": symbol_id}}


async def disable_symbol_liquidity(symbol_id: SymbolId):
    await liquidity_engine.detach(symbol_id)
    return {"status": "ok", "data": {"symbol_id": symbol_id}}


async def handle_ticker_event(event):
    logger.info("Handling ticker event")
    data = {
        "event_type": "ticker",
        "symbol_id": event["s"],
        "price": event["c"],
    }
    await ws_manager.broadcast(data)
    await liquidity_engine.update_symbol(data)


events_map = {"24hrMiniTicker": handle_ticker_event}
