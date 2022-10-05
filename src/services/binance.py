import logging

from src.handlers import binance
from src.models.symbol import SymbolId
from src.utils.binance_liquidity_engine import get_binance_liquidity_engine
from src.utils.ws_manager import get_ws_manager

logger = logging.getLogger(__name__)

ws_manager = get_ws_manager()
liquidity_engine = get_binance_liquidity_engine()


logger = logging.getLogger(__name__)

async def get_tickers():
    response = {}
    try:
        response = await binance.get_tickers('["BTCBUSD","BTCUSDT"]')
    except Exception:
        logger.error("Error getting tickers")
    return response

async def get_balances():
    response = {}
    try:
        account = await binance.get_account()
        response = account["balances"]
    except Exception:
        logger.error("Error getting balances")
    return response

async def enable_symbol_liquidity(symbol_id: SymbolId):
    await liquidity_engine.attach(symbol_id)
    return {"status": "ok", "data": {"symbol_id": symbol_id}}


async def disable_symbol_liquidity(symbol_id: SymbolId):
    await liquidity_engine.detach(symbol_id)
    return {"status": "ok", "data": {"symbol_id": symbol_id}}


async def handle_ticker_event(event):
    logger.debug("Handling ticker event")
    data = {
        "event_type": "ticker",
        "symbol_id": event["s"],
        "price": event["c"],
    }
    # Add the data to the liquidity engine prior to notifying the client with new data
    await liquidity_engine.update_symbol(data)



events_map = {"24hrMiniTicker": handle_ticker_event}
