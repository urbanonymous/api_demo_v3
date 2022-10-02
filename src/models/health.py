from pydantic import BaseModel


class Health(BaseModel):
    timestamp: float
