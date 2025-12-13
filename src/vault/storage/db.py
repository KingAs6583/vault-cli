"""VaultDB: Provides a lightweight, secure wrapper over SQLite for storing
encrypted secrets and file blobs in a local encrypted vault.

This module handles DB schema creation, WAL mode for concurrency, and
add/get/cleanup operations for secrets and file blobs.
"""

import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from vault.crypto.aes import decrypt, encrypt
from vault.crypto.kdf import derive_key, generate_salt
from vault.exceptions import StorageError
from vault.storage.models import SecretRecord


class VaultDB:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # Set a reasonable timeout and enable WAL for better concurrency
        self.conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA foreign_keys = ON;")
        except Exception:
            # If PRAGMA fails, continue but it should be logged elsewhere
            pass
        self._create_table()
        # Best-effort: restrict DB file permissions on POSIX
        try:
            os.chmod(self.db_path, 0o600)
        except Exception:
            pass
        # Apply migrations (if any) — migrations are idempotent and may upgrade
        # older DBs to the current schema.
        try:
            from vault.storage.migrations import apply_migrations

            apply_migrations(self.conn)
        except Exception:
            # Migration failures shouldn't silently prevent the DB from being usable,
            # but they should be reported; for now this is a best-effort, and tests
            # can handle errors otherwise.
            pass

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _create_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS secrets (
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
                """
            )
            # Index for faster lookup by project and environment
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_secrets_proj_env ON secrets(project, environment)"
            )
            self.conn.commit()
        except Exception as e:
            raise StorageError(f"Failed to create table: {e}")

    def add_secret(self, record: SecretRecord):
        try:
            # Preserve created_at on update using ON CONFLICT DO UPDATE pattern
            self.conn.execute(
                """
                INSERT INTO secrets
                (project, environment, key, value, iv, salt, created_at, updated_at, is_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project, environment, key)
                DO UPDATE SET
                    value=excluded.value,
                    iv=excluded.iv,
                    salt=excluded.salt,
                    updated_at=excluded.updated_at,
                    is_file=excluded.is_file
                """,
                (
                    record.project,
                    record.environment,
                    record.key,
                    record.value,
                    record.iv,
                    record.salt,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                    int(record.is_file),
                ),
            )
            self.conn.commit()
        except Exception as e:
            raise StorageError(f"Failed to add secret: {e}")

    def get_secret(
        self, project: str, environment: str, key: str
    ) -> SecretRecord | None:
        try:
            cursor = self.conn.execute(
                """
                SELECT project, environment, key, value, iv, salt, created_at, updated_at, is_file
                FROM secrets
                WHERE project=? AND environment=? AND key=?
                """,
                (project, environment, key),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return SecretRecord(
                project=row[0],
                environment=row[1],
                key=row[2],
                value=row[3],
                iv=row[4],
                salt=row[5],
                created_at=datetime.fromisoformat(row[6]),
                updated_at=datetime.fromisoformat(row[7]),
                is_file=bool(row[8]),
            )
        except Exception as e:
            raise StorageError(f"Failed to retrieve secret: {e}")

    def add_file_secret(
        self,
        project: str,
        environment: str,
        key: str,
        filepath: str,
        master_password: str,
    ):
        """
        Encrypt a file (e.g., .jks) and store it in the vault DB.

        :param project: Project name
        :param environment: Environment name (dev/prod)
        :param key: Secret key name
        :param filepath: Path to the file to encrypt
        :param master_password: Master password for key derivation
        """
        path = Path(filepath)
        if not path.exists() or not path.is_file():
            raise StorageError(f"File {filepath} does not exist")

        data = path.read_bytes()
        salt = generate_salt()
        key_bytes = derive_key(master_password, salt)
        iv, ciphertext = encrypt(key_bytes, data)

        record = SecretRecord(
            project=project,
            environment=environment,
            key=key,
            value=ciphertext,
            iv=iv,
            salt=salt,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_file=True,
        )
        self.add_secret(record)

    def get_file_secret(
        self,
        project: str,
        environment: str,
        key: str,
        master_password: str,
        output_dir: str | None = None,
    ) -> Path:
        """
        Decrypt a file secret and write it to a temporary file.

        :param project: Project name
        :param environment: Environment name
        :param key: Secret key name
        :param master_password: Master password for key derivation
        :param output_dir: Optional directory for temp file
        :return: Path to the decrypted temporary file
        """
        record = self.get_secret(project, environment, key)
        if not record or not record.is_file:
            raise StorageError(
                f"No file secret found for {project}/{environment}/{key}"
            )

        key_bytes = derive_key(master_password, record.salt)
        plaintext = decrypt(key_bytes, record.iv, record.value)

        temp_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir())
        # Use key (which is the original filename) to restore name and extension
        orig_name = record.key
        safe_name = Path(orig_name).name
        suffix = Path(safe_name).suffix or ".tmp"
        prefix = f"vault_{Path(safe_name).stem}_"

        # Create a secure temporary file with mode 0o600 using os.open
        fd, name = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=temp_dir)
        try:
            # Set strict permissions (rw-------)
            try:
                os.fchmod(fd, 0o600)
            except Exception:
                # os.fchmod may not be available on some systems; fallback to chmod
                try:
                    os.chmod(name, 0o600)
                except Exception:
                    # Best effort; proceed
                    pass

            with os.fdopen(fd, "wb") as f:
                f.write(plaintext)
                f.flush()

            return Path(name)
        except Exception as e:
            # Ensure file descriptor is closed and file is removed on error
            try:
                os.close(fd)
            except Exception:
                pass
            try:
                Path(name).unlink()
            except Exception:
                pass
            raise StorageError(f"Failed to write temp file: {e}")

    def cleanup_temp_file(self, filepath: str):
        """
        Securely delete a temporary file after use.
        Note: Secure deletion cannot be guaranteed on all filesystems (SSD, snapshots).
        """
        path = Path(filepath)
        if path.exists():
            try:
                # Overwrite in chunks and then delete
                chunk_size = 1024 * 1024  # 1 MB
                size = path.stat().st_size
                with open(path, "r+b") as f:
                    f.seek(0)
                    remaining = size
                    zero_chunk = b"\x00" * min(chunk_size, remaining)
                    while remaining > 0:
                        write_size = min(chunk_size, remaining)
                        f.write(zero_chunk[:write_size])
                        remaining -= write_size
                    f.flush()
                try:
                    path.unlink()
                except Exception:
                    # If delete fails, leave a warning to the caller
                    raise
            except Exception as e:
                raise StorageError(f"Failed to cleanup temp file {filepath}: {e}")
