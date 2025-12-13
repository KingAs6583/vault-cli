from dataclasses import dataclass
from datetime import datetime


@dataclass
class SecretRecord:
    project: str
    environment: str
    key: str
    value: bytes  # encrypted bytes
    iv: bytes
    salt: bytes
    created_at: datetime
    updated_at: datetime
    is_file: bool = False  # distinguish file vs string
