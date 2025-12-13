import os
from hashlib import pbkdf2_hmac

from vault.constants import (
    AES_KEY_LENGTH,
    KDF_ITERATIONS,
    KDF_SALT_LENGTH,
    MIN_PASSWORD_LENGTH,
)
from vault.exceptions import InvalidPasswordError

"""KDF helpers for deriving AES keys from passphrases.

Currently uses PBKDF2-HMAC-SHA256 with a per-secret salt. Consider migrating
to Argon2 for improved resistance to GPU attacks in the future.
"""


def generate_salt() -> bytes:
    """
    Generate a cryptographically secure random salt.
    """
    return os.urandom(KDF_SALT_LENGTH)


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a symmetric encryption key from a password using PBKDF2.
    """

    if not password or len(password) < MIN_PASSWORD_LENGTH:
        raise InvalidPasswordError("Password too short")

    return pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=salt,
        iterations=KDF_ITERATIONS,
        dklen=AES_KEY_LENGTH,
    )
