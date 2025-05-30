import uuid
import psycopg2
from psycopg2.extras import execute_batch
import datetime

class DBQueue:
    """Simple PostgreSQL queue for password candidates."""
    def __init__(self, db_uri, batch_size=1000, worker_id=None):
        self.conn = psycopg2.connect(db_uri)
        self.batch_size = batch_size
        self.worker_id = worker_id or str(uuid.uuid4())
        self.ensure_table()

    def ensure_table(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS password_queue (
                    password TEXT PRIMARY KEY,
                    status TEXT NOT NULL DEFAULT 'pending',
                    claimed_by TEXT,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            self.conn.commit()

    def fetch_batch(self):
        """Claim a batch of pending passwords and return them."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE password_queue
                   SET status='in_progress', claimed_by=%s, timestamp=NOW()
                 WHERE password IN (
                        SELECT password FROM password_queue
                         WHERE status='pending'
                         LIMIT %s
                         FOR UPDATE SKIP LOCKED
                 )
              RETURNING password
                """,
                (self.worker_id, self.batch_size),
            )
            rows = cur.fetchall()
            self.conn.commit()
            return [r[0] for r in rows]

    def mark_tested(self, passwords):
        if not passwords:
            return
        with self.conn.cursor() as cur:
            execute_batch(
                cur,
                "UPDATE password_queue SET status='tested', timestamp=NOW() WHERE password=%s",
                [(p,) for p in passwords],
            )
            self.conn.commit()

    def mark_found(self, password):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE password_queue SET status='found', timestamp=NOW() WHERE password=%s",
                (password,),
            )
            self.conn.commit()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
