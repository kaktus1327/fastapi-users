from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LogLine(BaseModel):
    host: str
    timestamp: datetime
    method: str
    return_status: int
    message: str


class User(BaseModel):
    id: UUID
    name: str
    age: int

