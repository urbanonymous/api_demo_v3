import hashlib
import hmac
import logging
import time
import json

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


async def get_tickers(symbols: list):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_API_URL}/ticker/price?symbols={json.dumps(symbols)}") as response:
            return await handle_response(response)


async def create_order(order_data):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_TESTNET_API_URL}/order", headers=HEADERS, data= await generate_signature(order_data)
        ) as response:
            return await handle_response(response)


async def cancel_orders(symbol_id: str):
    data = {"symbol": symbol_id.upper(), "timestamp": int(time.time() * 1000)}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_TESTNET_API_URL}/openOrders", headers=HEADERS, data=data) as response:
            return await handle_response(response)


async def get_balances():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{BASE_TESTNET_API_URL}/account", headers=HEADERS, params= await generate_signature({})
        ) as response:
            return await handle_response(response)
