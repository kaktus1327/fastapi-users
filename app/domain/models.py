import copy
from dataclasses import dataclass, field, is_dataclass, replace
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

try:
    from cassandra_2026.systems.user_logs.models import LogLine, User

    OWNED_MODELS = False
except ModuleNotFoundError:

    @dataclass
    class User:
        name: str
        age: int
        id: UUID = field(default_factory=uuid4)

    @dataclass
    class LogLine:
        host: str
        method: str
        return_status: str
        message: str
        timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
        id: UUID = field(default_factory=uuid4)

    OWNED_MODELS = True


def new_user_id() -> UUID:
    return uuid4()


def apply_changes(user: Any, **changes: Any) -> Any:
    if is_dataclass(user):
        try:
            return replace(user, **changes)
        except TypeError:
            pass
    clone = copy.copy(user)
    for name, value in changes.items():
        setattr(clone, name, value)
    return clone


__all__ = ["LogLine", "OWNED_MODELS", "User", "apply_changes", "new_user_id"]
