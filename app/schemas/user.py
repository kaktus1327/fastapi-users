from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

Name = Annotated[str, Field(min_length=1, max_length=100)]
Age = Annotated[int, Field(ge=0, le=150)]


def _strip_name(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("name must not be blank")
    return stripped


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Name
    age: Age

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _strip_name(value)


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Name | None = None
    age: Age | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return None if value is None else _strip_name(value)


class UserRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    name: str
    age: int
