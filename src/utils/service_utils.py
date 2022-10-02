import logging
from contextlib import asynccontextmanager

from fastapi import HTTPException, status
from pydantic.error_wrappers import ValidationError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def handle_service_response():
    try:
        yield

    except HTTPException:
        raise

    except ValidationError as ex:
        raise HTTPException(status_code=422, detail=ex.json())

    except BaseException as ex:
        logger.exception(ex)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "internal error") from ex
