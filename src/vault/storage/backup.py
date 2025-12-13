import shutil
from pathlib import Path
from datetime import datetime
from vault.logging import setup_logger
from vault.crypto.kdf import derive_key, generate_salt
from vault.crypto.aes import encrypt
from vault.crypto.kdf import derive_key
from vault.crypto.aes import decrypt
from pathlib import Path

logger = setup_logger("vault-backup")


def backup_db(db_path: str, backup_dir: str = "vault-backups") -> Path:
    """
    Backup the vault DB to a timestamped file in backup_dir.

    :param db_path: Path to vault.db
    :param backup_dir: Directory to store backups
    :return: Path to backup file
    """
    src = Path(db_path)
    if not src.exists():
        raise FileNotFoundError(f"DB not found at {db_path}")

    backup_folder = Path(backup_dir)
    backup_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_folder / f"vault_backup_{timestamp}.db"

    shutil.copy2(src, backup_file)
    logger.info(f"Vault DB backed up to {backup_file}")
    return backup_file

def encrypt_backup(backup_path: str, master_password: str) -> Path:
    """
    Encrypt backup DB file using master password.

    :param backup_path: Path to DB backup
    :param master_password: Master password for encryption
    :return: Path to encrypted file
    """
    path = Path(backup_path)
    data = path.read_bytes()

    salt = generate_salt()
    key_bytes = derive_key(master_password, salt)
    iv, ciphertext = encrypt(key_bytes, data)

    encrypted_file = path.with_suffix(".enc")
    # Save salt + iv + ciphertext
    with open(encrypted_file, "wb") as f:
        f.write(salt + iv + ciphertext)

    return encrypted_file

def decrypt_backup(encrypted_file: str, master_password: str) -> Path:
    """
    Decrypt encrypted DB backup.

    :param encrypted_file: Path to .enc file
    :param master_password: Master password
    :return: Path to decrypted DB file
    """
    path = Path(encrypted_file)
    data = path.read_bytes()

    salt_len = 16
    iv_len = 12

    salt = data[:salt_len]
    iv = data[salt_len:salt_len+iv_len]
    ciphertext = data[salt_len+iv_len:]

    key_bytes = derive_key(master_password, salt)
    plaintext = decrypt(key_bytes, iv, ciphertext)

    decrypted_file = path.with_suffix(".db")
    decrypted_file.write_bytes(plaintext)
    return decrypted_file