#!/usr/bin/env python
"""Create the PostgreSQL `password_queue` table."""

import argparse
import sys
import psycopg2


def create_table(conn):
    with conn.cursor() as cur:
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
    conn.commit()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create password database")
    parser.add_argument(
        "--db-uri",
        required=True,
        help="PostgreSQL connection URI",
    )
    args = parser.parse_args(argv)

    conn = psycopg2.connect(args.db_uri)
    create_table(conn)
    conn.close()


if __name__ == "__main__":
    main()


