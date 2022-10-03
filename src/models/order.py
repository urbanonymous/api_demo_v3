from enum import Enum

from pydantic import BaseModel


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Order(BaseModel):
    """The order data is simplified"""

    symbol_id: str
    price: float
    side: Side
    order_id: str
    order_type: str  # Binance API doesn't specify all enum types
