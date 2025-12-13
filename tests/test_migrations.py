import sqlite3
from pathlib import Path
from vault.storage.db import VaultDB


def test_migration_adds_filename_column(tmp_path):
    # Create an older-style DB (without filename column)
    db_path = tmp_path / "old_vault.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE secrets (
            project TEXT NOT NULL,
            environment TEXT NOT NULL,
            key TEXT NOT NULL,
            value BLOB NOT NULL,
            iv BLOB NOT NULL,
            salt BLOB NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_file INTEGER NOT NULL,
            PRIMARY KEY(project, environment, key)
        )
    ''')
    conn.commit()
    conn.close()

    # Now, initialize VaultDB — it should apply migrations
    VaultDB(str(db_path))

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info('secrets')")
    columns = {row[1] for row in cur.fetchall()}
    conn.close()

    assert 'filename' in columns
