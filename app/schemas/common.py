from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

ItemT = TypeVar("ItemT")


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location: list[str]
    message: str
    type: str


class ErrorPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: ErrorPayload


class Page(BaseModel, Generic[ItemT]):
    model_config = ConfigDict(extra="forbid")

    items: list[ItemT]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class HealthStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str


class ReadinessStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    checks: dict[str, str]
