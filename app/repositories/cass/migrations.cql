CREATE KEYSPACE IF NOT EXISTS app
  WITH replication = {'class':'NetworkTopologyStrategy','dc1':1};

CREATE TABLE IF NOT EXISTS app.users (
    id   uuid PRIMARY KEY,
    name text,
    age  int
);

CREATE TABLE IF NOT EXISTS app.request_logs (
    host        text,       -- app instance that served the request
    hour_bucket text,       -- 'YYYY-MM-DDTHH', UTC, e.g. '2026-09-04T13'
    method      text,       -- uppercase: GET, POST, PUT, DELETE, PATCH
    ts          timestamp,  -- UTC, response completion time
    log_id      uuid,       -- uuid4, tiebreaker only
    status      text,
    message     text,
    PRIMARY KEY ((host, hour_bucket, method), ts, log_id)
) WITH CLUSTERING ORDER BY (ts DESC, log_id ASC)
  AND default_time_to_live = 604800          -- 7 days
  AND gc_grace_seconds = 3600
  AND compaction = {'class':'TimeWindowCompactionStrategy',
                    'compaction_window_unit':'HOURS',
                    'compaction_window_size':1};