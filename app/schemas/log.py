from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HTTPMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


Host = Annotated[str, Field(min_length=1, max_length=255)]
ReturnStatus = Annotated[str, Field(pattern=r"^[1-5]\d{2}$")]
Message = Annotated[str, Field(max_length=2000)]


class LogLineCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: Host
    timestamp: datetime | None = None
    method: HTTPMethod
    return_status: ReturnStatus
    message: Message

    @field_validator("host")
    @classmethod
    def normalize_host(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("host must not be blank")
        return stripped


class LogLineRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    host: str
    timestamp: datetime
    method: HTTPMethod
    return_status: str
    message: str
