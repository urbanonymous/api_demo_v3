import requests
import hashlib
import hmac
import time

TESTNET_API_KEY = "<key>"
TESTNET_SECRET_KEY = "<secret>"
TICKER = "BTCUSDT"

BASE_API_URL = "https://api.binance.com/api/v3"
BASE_TESTNET_API_URL = "https://testnet.binance.vision/api/v3"

TICKER = "BTCUSDT"
SPREAD = 100

HEADERS = {'X-MBX-APIKEY': TESTNET_API_KEY }

def generate_signature(data: dict) -> str:
    data['timestamp'] = int(time.time() * 1000)
    query_string = '&'.join([f"{key}={value}" for key, value in data.items()])
    m = hmac.new(TESTNET_SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
    data['signature'] = m.hexdigest()
    return data

r = requests.get(f"{BASE_API_URL}/ticker/price?symbol={TICKER}")
current_price = r.json()["price"]
print(f"The current price of {TICKER} is {current_price}")


r = requests.get(f"{BASE_TESTNET_API_URL}/account", headers=HEADERS, params=generate_signature({}))
balances = {coin["asset"] : coin["free"]  for coin in r.json()["balances"]}
print(f"Account balances related: BTC {balances['BTC']}, USDT {balances['USDT']}")


print("Placing bid and ask orders to provide liquidity")

order_data = {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "price": float(current_price) - SPREAD,
    "quantity": 0.05,
    "timeInForce": "GTC",
}
 
r = requests.post(f"{BASE_TESTNET_API_URL}/order", headers=HEADERS, data=generate_signature(order_data))
buy_oder_data = r.json()
print(f"A new {buy_oder_data['symbol']} buy order has been placed: {buy_oder_data['origQty']} @ {buy_oder_data['price']}")

order_data = {
    "symbol": "BTCUSDT",
    "side": "SELL",
    "type": "LIMIT",
    "price": float(current_price) + SPREAD,
    "quantity": 0.05,
    "timeInForce": "GTC",
}
 
r = requests.post(f"{BASE_TESTNET_API_URL}/order", headers=HEADERS, data=generate_signature(order_data))
buy_oder_data = r.json()
print(f"A new {buy_oder_data['symbol']} sell order has been placed: {buy_oder_data['origQty']} @ {buy_oder_data['price']}")

