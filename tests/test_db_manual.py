from datetime import datetime
from pathlib import Path

from vault.storage.db import VaultDB
from vault.storage.models import SecretRecord

# Temporary DB file
db_path = Path("project-metadata/data/vault.db")
db_path.parent.mkdir(parents=True, exist_ok=True)

db = VaultDB(str(db_path))

# Test secret
record = SecretRecord(
    project="myapp",
    environment="dev",
    key="API_KEY",
    value=b"encrypted_data_here",
    iv=b"iv_bytes",
    salt=b"salt_bytes",
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow(),
    is_file=False,
)

db.add_secret(record)
retrieved = db.get_secret("myapp", "dev", "API_KEY")

assert retrieved.key == "API_KEY"
assert retrieved.value == b"encrypted_data_here"
print("DB test passed.")
