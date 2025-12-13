import sqlite3
from datetime import datetime
from pathlib import Path
import tempfile

from vault.storage.models import SecretRecord
from vault.exceptions import StorageError
from vault.crypto.aes import encrypt, decrypt
from vault.crypto.kdf import derive_key, generate_salt


class VaultDB:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

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
            self.conn.commit()
        except Exception as e:
            raise StorageError(f"Failed to create table: {e}")

    def add_secret(self, record: SecretRecord):
        try:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO secrets
                (project, environment, key, value, iv, salt, created_at, updated_at, is_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
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
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, dir=temp_dir, prefix="vault_", suffix=".tmp"
        )
        temp_file.write(plaintext)
        temp_file.close()

        return Path(temp_file.name)

    def cleanup_temp_file(self, filepath: str):
        """
        Securely delete a temporary file after use.
        """
        path = Path(filepath)
        if path.exists():
            try:
                # Overwrite and delete
                with open(path, "ba+") as f:
                    length = f.tell()
                    f.seek(0)
                    f.write(b"\x00" * length)
                path.unlink()
            except Exception as e:
                raise StorageError(f"Failed to cleanup temp file {filepath}: {e}")
