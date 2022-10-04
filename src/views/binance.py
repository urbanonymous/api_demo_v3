import asyncio
import logging

from fastapi import APIRouter, WebSocket

from src.models.symbol import SymbolId
from src.services import binance as service
from src.utils.service_utils import handle_service_response
from src.utils.ws_manager import get_ws_manager

router = APIRouter()
ws_manager = get_ws_manager()

logger = logging.getLogger(__name__)


@router.post("/symbol/{symbol_id}", name="enable symbol liquidity", status_code=200)
async def enable_symbol_liquidity(symbol_id: SymbolId):

    async with handle_service_response():
        return await service.enable_symbol_liquidity(symbol_id=symbol_id)


@router.delete("/symbol/{symbol_id}", name="disable symbol liquidity", status_code=200)
async def disable_ticker_liquidity(symbol_id: SymbolId):
    async with handle_service_response():
        return await service.disable_symbol_liquidity(symbol_id=symbol_id)


@router.websocket("/ws")
async def connect_ws(
    websocket: WebSocket,
):
    await websocket.accept()
    logger.info("Client connected to websocket")
    async with ws_manager.add_connection(websocket):
        try:
            while websocket in ws_manager.active_connections:
                try:
                    message = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=5,
                    )
                    logger.info(message)
                except Exception:
                    pass

        except Exception as e:
            logger.exception(e)
    logger.info("Websocket connection closed")
