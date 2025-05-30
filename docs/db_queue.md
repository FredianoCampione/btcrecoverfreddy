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
    --db-batch-size 500
```

Each fetched password is marked `in_progress`. After testing, entries are updated to `tested`. When a correct password is found the row is marked `found`.
