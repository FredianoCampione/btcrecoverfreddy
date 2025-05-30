# Password Database

These helper scripts make it easy to store large password lists in a PostgreSQL
database.  They can be useful when distributing password testing across
multiple machines or when you want to pre-process lists before running
`btcrecover`.

## Initialising the Database

1. Ensure the Python package `psycopg2` (or `psycopg2-binary`) is installed.
2. Create a new PostgreSQL database and user if required.
3. Run the following command to create the required table:

```
python scripts/create_password_db.py --db-uri postgresql://USER:PASS@HOST/DBNAME
```

This will create a table named `password_queue` with columns for the password,
its `status` (initially `pending`), the worker that claimed it, and a timestamp.

## Loading Passwords

Use `add_passwords.py` to insert passwords from a file or from standard input.
Duplicate passwords are ignored automatically.

```
python scripts/add_passwords.py --db-uri postgresql://USER:PASS@HOST/DBNAME passwords.txt
```

You can also read from standard input and control how many records are inserted
at once using `--batch-size` (defaults to 1000):

```
cat biglist.txt | python scripts/add_passwords.py --db-uri postgresql://... --batch-size 5000
```

All inserted rows will have their `status` set to `pending`.

To automatically retry jobs that were claimed but never completed, use the
`--db-expire-hours` option when running `btcrecover` or call
`DBQueue.reset_expired()` from your own scripts.

