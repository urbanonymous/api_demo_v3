from datetime import datetime

from fastapi import APIRouter

from src.models.health import Health

router = APIRouter()


@router.get("/health", name="health", response_model=Health, status_code=200)
def healthcheck() -> Health:
    return Health(timestamp=datetime.now().timestamp())
