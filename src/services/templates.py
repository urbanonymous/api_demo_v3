import logging

from src.handlers import binance

logger = logging.getLogger(__name__)


async def generate_index_data():
    return {
        "user_data": await binance.get_balances(), 
        "tickers_data": await binance.get_tickers(["BTCUSD", "BTCUSDT"]),
    }
    
