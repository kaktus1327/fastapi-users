import threading
from datetime import datetime
from uuid import UUID

from app.domain.models import LogLine


class InMemoryLogRepository:
    def __init__(self) -> None:
        self._logs: dict[str, LogLine] = {}
        self._lock = threading.Lock()

    def add(self, log: LogLine) -> LogLine:
        with self._lock:
            self._logs[str(log.id)] = log
            return log

    def get(self, log_id: UUID) -> LogLine | None:
        with self._lock:
            return self._logs.get(str(log_id))

    def list(
        self,
        host: str | None = None,
        method: str | None = None,
        return_status: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[LogLine]:
        with self._lock:
            logs = list(self._logs.values())
        matched = [
            log
            for log in logs
            if (host is None or log.host == host)
            and (method is None or log.method == method)
            and (return_status is None or log.return_status == return_status)
            and (since is None or log.timestamp >= since)
            and (until is None or log.timestamp <= until)
        ]
        return sorted(matched, key=lambda log: log.timestamp, reverse=True)
