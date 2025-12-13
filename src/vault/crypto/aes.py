import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from vault.constants import AES_GCM_IV_LENGTH, AES_KEY_LENGTH
from vault.exceptions import CryptoError


def encrypt(key: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    """
    Encrypt data using AES-256-GCM.
    Returns (iv, ciphertext).
    """

    if len(key) != AES_KEY_LENGTH:
        raise CryptoError("Invalid AES key length")

    iv = os.urandom(AES_GCM_IV_LENGTH)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, None)

    return iv, ciphertext


def decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """
    Decrypt AES-256-GCM encrypted data.
    Raises exception if authentication fails.
    """

    if len(key) != AES_KEY_LENGTH:
        raise CryptoError("Invalid AES key length")

    if len(iv) != AES_GCM_IV_LENGTH:
        raise CryptoError("Invalid IV length")

    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(iv, ciphertext, None)
    except Exception as exc:
        # Avoid leaking internal errors; present a redacted message.
        raise CryptoError("Decryption failed") from exc
