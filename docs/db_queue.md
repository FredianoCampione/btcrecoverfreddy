# Using PostgreSQL for password queues

BTCRecover can source candidate passwords from a PostgreSQL database. Provide the database connection using `--db-uri`.
Passwords will be claimed in batches configured via `--db-batch-size`.

Create a table matching this schema:

```
CREATE TABLE password_queue (
    password TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending',
    claimed_by TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

Example usage:

```
python3 btcrecover.py --wallet wallet.dat \
    --db-uri postgresql://user:pass@localhost/dbname \
    --db-batch-size 500 \
    --db-expire-hours 12
```

Each fetched password is marked `in_progress`. After testing, entries are updated to `tested`. When a correct password is found the row is marked `found`.

## Requeuing stale rows

Use `--db-expire-hours` to reset any `in_progress` rows whose timestamp is older
than the specified number of hours. BTCRecover performs this cleanup when it
starts so that stale entries from crashed workers are retried.

You can also run the cleanup manually from a scheduled task:

```
python3 -c "from utilities.db_queue import DBQueue; DBQueue('postgresql://user:pass@localhost/dbname').reset_expired(24)"
```
