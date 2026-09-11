from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models import LogLine


class PersistentLogger(ABC):

    def __init__(self, db: LogStore):
        pass

    @abstractmethod
    def get_logger(self):
        # returns a logger semantically equivalent to `loguru.logger`
        pass


class LogStore(ABC):

    @abstractmethod
    def store_line(self, line: LogLine):
        pass