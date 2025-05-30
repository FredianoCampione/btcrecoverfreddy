#!/usr/bin/env python
"""Load password lists into PostgreSQL."""

import argparse
import sys
import psycopg2
from psycopg2.extras import execute_values


def insert_passwords(conn, passwords, batch_size=1000):
    with conn.cursor() as cur:
        for i in range(0, len(passwords), batch_size):
            batch = [(p,) for p in passwords[i:i+batch_size]]
            execute_values(
                cur,
                "INSERT INTO passwords(password) VALUES %s ON CONFLICT DO NOTHING",
                batch,
            )
    conn.commit()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Insert passwords into database")
    parser.add_argument("--db-uri", required=True, help="PostgreSQL connection URI")
    parser.add_argument("file", nargs="?", help="File with passwords (defaults to stdin)")
    parser.add_argument("--batch-size", type=int, default=1000, help="Insert batch size")
    args = parser.parse_args(argv)

    fh = open(args.file, "r", encoding="utf-8") if args.file else sys.stdin
    conn = psycopg2.connect(args.db_uri)

    passwords = []
    for line in fh:
        pw = line.rstrip("\n")
        if pw:
            passwords.append(pw)
            if len(passwords) >= args.batch_size:
                insert_passwords(conn, passwords, batch_size=args.batch_size)
                passwords = []

    if passwords:
        insert_passwords(conn, passwords, batch_size=args.batch_size)

    conn.close()
    if fh is not sys.stdin:
        fh.close()


if __name__ == "__main__":
    main()


