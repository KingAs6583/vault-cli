from datetime import datetime, timezone

from vault.storage.db import VaultDB
from vault.storage.models import SecretRecord


def test_db_add_and_get_secret(tmp_path):
    db_path = tmp_path / "vault.db"
    db = VaultDB(str(db_path))

    record = SecretRecord(
        project="myapp",
        environment="dev",
        key="API_KEY",
        value=b"encrypted_data_here",
        iv=b"iv_bytes",
        salt=b"salt_bytes",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_file=False,
    )

    db.add_secret(record)
    retrieved = db.get_secret("myapp", "dev", "API_KEY")

    assert retrieved.key == "API_KEY"
    assert retrieved.value == b"encrypted_data_here"
