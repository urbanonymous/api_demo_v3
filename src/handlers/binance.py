import hashlib
import hmac
import logging
import time

import aiohttp

from src.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

BASE_API_URL = "https://api.binance.com/api/v3"
BASE_TESTNET_API_URL = "https://testnet.binance.vision/api/v3"

HEADERS = {"X-MBX-APIKEY": settings.testnet_api_key}


async def handle_response(response):
    if response.status == 200:
        return await response.json()
    text = await response.text()
    logging.warning(text)
    raise Exception(f"Response different than 200 status, {response.status}")


async def generate_signature(data: dict) -> str:
    data["timestamp"] = int(time.time() * 1000)
    query_string = "&".join([f"{key}={value}" for key, value in data.items()])
    m = hmac.new(settings.testnet_secret_key.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256)
    data["signature"] = m.hexdigest()
    return data


async def get_tickers(symbols: str):
    # Using str instead of list due python str(list) produces ilegal symbols for Binance API
    logger.info(f"Getting tickers for {symbols}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_API_URL}/ticker/price?symbols={symbols}") as response:
            data = await handle_response(response)
            return {symbol["symbol"]: round(float(symbol["price"]), 2) for symbol in data}

async def create_order(order_data):
    logger.info(f"Creating order: {order_data}")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_TESTNET_API_URL}/order", headers=HEADERS, data=await generate_signature(order_data)
        ) as response:
            return await handle_response(response)


async def cancel_orders(symbol_id: str):
    logger.indo(f"Cancelling all orders for {symbol_id}")
    data = {"symbol": symbol_id.upper(), "timestamp": int(time.time() * 1000)}
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{BASE_TESTNET_API_URL}/openOrders", headers=HEADERS, data=await generate_signature(data)
        ) as response:
            return await handle_response(response)


async def get_account():
    logger.info("Getting account data")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{BASE_TESTNET_API_URL}/account", headers=HEADERS, params=await generate_signature({})
        ) as response:
            return await handle_response(response)
