from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Query

from app.core.config import Settings, get_settings
from app.ports.user_repository import UserRepository
from app.repositories.log_memory import InMemoryLogRepository
from app.repositories.memory import MemoryUserRepository
from app.services.logs import LogService
from app.services.users import UserService

_user_repository: UserRepository = MemoryUserRepository()
_log_repository = InMemoryLogRepository()


def set_user_repository(repository: UserRepository) -> None:
    global _user_repository
    _user_repository = repository


def get_user_repository() -> UserRepository:
    return _user_repository


def get_log_repository() -> InMemoryLogRepository:
    return _log_repository


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)


def get_log_service(
    repository: Annotated[InMemoryLogRepository, Depends(get_log_repository)],
) -> LogService:
    return LogService(repository)


ReadinessCheck = Callable[[], Awaitable[None]]

_readiness_checks: dict[str, ReadinessCheck] = {
    "user_repository": lambda: UserService(get_user_repository()).ping(),
}


def register_readiness_check(name: str, check: ReadinessCheck) -> None:
    _readiness_checks[name] = check


def get_readiness_checks() -> dict[str, ReadinessCheck]:
    return dict(_readiness_checks)


class Pagination:
    def __init__(self, limit: int, offset: int) -> None:
        self.limit = limit
        self.offset = offset


def get_pagination(
    settings: Annotated[Settings, Depends(get_settings)],
    limit: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Pagination:
    resolved = settings.default_page_size if limit is None else min(limit, settings.max_page_size)
    return Pagination(limit=resolved, offset=offset)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
LogServiceDep = Annotated[LogService, Depends(get_log_service)]
PaginationDep = Annotated[Pagination, Depends(get_pagination)]
