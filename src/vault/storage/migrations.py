"""Database migrations for the Vault SQLite schema.

This module implements a tiny migrations framework: a `migrations` table records
applied migration names and each migration is idempotent so it can be re-run
against an existing DB.
"""
from datetime import datetime, timezone
import sqlite3


MIGRATIONS = []


def migration(name):
    def _decorator(fn):
        MIGRATIONS.append((name, fn))
        return fn

    return _decorator


def ensure_migrations_table(conn: sqlite3.Connection):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            applied_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def get_applied(conn: sqlite3.Connection) -> set:
    cursor = conn.execute("SELECT name FROM migrations")
    return {row[0] for row in cursor.fetchall()}


def record_applied(conn: sqlite3.Connection, name: str):
    conn.execute(
        "INSERT INTO migrations (name, applied_at) VALUES (?, ?)",
        (name, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()


@migration("0001_add_filename_column")
def add_filename_column(conn: sqlite3.Connection):
    """Add an optional `filename` column to `secrets` to record original filenames.

    The column is nullable and ignored if it already exists.
    """
    try:
        conn.execute("ALTER TABLE secrets ADD COLUMN filename TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        # Column probably already exists — ignore
        pass


def apply_migrations(conn: sqlite3.Connection):
    ensure_migrations_table(conn)
    applied = get_applied(conn)
    for name, fn in MIGRATIONS:
        if name in applied:
            continue
        fn(conn)
        record_applied(conn, name)
