import os
import uuid
from datetime import datetime, timezone

from cassandra.query import PreparedStatement
from dotenv import load_dotenv

from app.domain.models import LogLine
from app.repositories.cass.common import get_cluster_session
from app.repositories.interface_logs import LogStore

from cassandra.cluster import Cluster, Session


from loguru import logger

_INSERT_CQL = """
              INSERT INTO app.request_logs (host, hour_bucket, method, ts, log_id, status, message)
              VALUES (?, ?, ?, ?, ?, ?, ?) \
              """

_HOUR_BUCKET_FMT = "%Y-%m-%dT%H"


def _as_utc(ts: datetime) -> datetime:
    """Naive timestamps are assumed to already be UTC; aware ones are converted."""
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


class CassandraLogRepository(LogStore):

    def __init__(self, session: Session) -> None:
        self._session = session
        self._insert: PreparedStatement = session.prepare(_INSERT_CQL)
        # Same partition key + ts + log_id on every retry, so a retried write
        # produces the identical row. Lets the driver retry and speculate freely.
        self._insert.is_idempotent = True

    def store_line(self, line: LogLine) -> None:
        ts = _as_utc(line.timestamp)
        self._session.execute(
            self._insert,
            (
                line.host,
                ts.strftime(_HOUR_BUCKET_FMT),
                line.method.upper(),
                ts,
                uuid.uuid4(),
                str(line.return_status),
                line.message,
            ),
        )


if __name__ == '__main__':
    cluster, session = get_cluster_session()
    logger.info("Connected to Cassandra")

    store = CassandraLogRepository(session)
    store.store_line(LogLine(host="localhost", method="GET", timestamp=datetime.now(),
                             return_status=200, message="Hello, world!"))

    cluster.shutdown()
    logger.info("Disconnected from Cassandra")
