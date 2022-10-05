from enum import Enum

from pydantic import BaseModel, Field


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Order(BaseModel):
    """Order data simplified"""

    symbol_id: str = Field(alias="symbol")
    price: float
    side: Side
    size: float = Field(alias="origQty")
    order_id: str = Field(alias="orderId")
    order_type: str = Field(alias="type")  # Binance API doesn't specify all types in the enum
