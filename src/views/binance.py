import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect

from src.services import binance as service
from src.utils.ws_manager import get_ws_manager

router = APIRouter()
ws_manager = get_ws_manager()

logger = logging.getLogger(__name__)


@router.get("/ticker/{ticker_id}", name="health", status_code=200)
async def get_ticker_data(ticker_id: str):
    return {"data": {}}


@router.post("/ticker/{ticker_id}", name="health", status_code=200)
async def run_ticker_liquidity(ticker_id: str):
    return {"data": {}}


@router.delete("/ticker/{ticker_id}", name="health", status_code=200)
async def stop_ticker_liquidity(ticker_id: str):
    return {"data": {}}


@router.websocket("/ws")
async def connect_ws(
    websocket: WebSocket,
):
    await websocket.accept()
    async with ws_manager.add_connection(websocket) as session:
        try:
            while websocket.open:
                try:

                    message = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=5,
                    )
                    logger.info(message)
                except asyncio.TimeoutError as e:
                    continue
                except json.decoder.JSONDecodeError as e:
                    pass
                except WebSocketDisconnect as e:
                    logger.warning(f"Websocket disconnected")
                    break

                except Exception as e:
                    logger.exception(e)
                    break

        except WebSocketDisconnect:
            logger.warn(f"WS Client disconnected")

        except Exception as e:
            logger.exception(e)
