#!/usr/bin/env python
"""Create PostgreSQL password database."""

import argparse
import sys
import psycopg2


def create_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS passwords (
                id SERIAL PRIMARY KEY,
                password TEXT UNIQUE,
                status TEXT NOT NULL DEFAULT 'pending',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


