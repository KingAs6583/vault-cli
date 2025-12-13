# vault/exceptions.py

class VaultError(Exception):
    """Base exception for vault-related errors."""


class CryptoError(VaultError):
    """Encryption / decryption failure."""


class InvalidPasswordError(VaultError):
    """Raised when password validation fails."""


class StorageError(VaultError):
    """Database or file storage errors."""
