from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from starlette.concurrency import run_in_threadpool

from app.core.errors import NotFoundError
from app.domain.models import LogLine
from app.schemas.log import LogLineCreate


@dataclass(frozen=True, slots=True)
class LogFilters:
    host: str | None = None
    method: str | None = None
    return_status: str | None = None
    since: datetime | None = None
    until: datetime | None = None


@dataclass(frozen=True, slots=True)
class LogPage:
    items: list[LogLine]
    total: int


class LogService:
    def __init__(self, repository: object) -> None:
        self._repository = repository

    async def create(self, payload: LogLineCreate) -> LogLine:
        log = LogLine(
            host=payload.host,
            method=payload.method.value,
            return_status=payload.return_status,
            message=payload.message,
            timestamp=_to_utc(payload.timestamp) if payload.timestamp else datetime.now(UTC),
        )
        await run_in_threadpool(self._repository.add, log)
        return log

    async def get(self, log_id: UUID) -> LogLine:
        log = await run_in_threadpool(self._repository.get, log_id)
        if log is None:
            raise NotFoundError(f"Log line {log_id} not found")
        return log

    async def list(self, filters: LogFilters, limit: int, offset: int) -> LogPage:
        logs = await run_in_threadpool(
            self._repository.list,
            filters.host,
            filters.method,
            filters.return_status,
            _to_utc(filters.since) if filters.since else None,
            _to_utc(filters.until) if filters.until else None,
        )
        return LogPage(items=logs[offset : offset + limit], total=len(logs))


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
