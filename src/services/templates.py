import logging

from src.handlers import binance

logger = logging.getLogger(__name__)


async def get_balances():
    account = await binance.get_account()
    return account["balances"]
    
