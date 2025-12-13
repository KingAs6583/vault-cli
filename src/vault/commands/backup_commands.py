import click
from pathlib import Path
from vault.crypto.utils import prompt_password
from vault.storage.backup import backup_db, encrypt_backup, decrypt_backup as decrypt_backup_fn
from vault.config import get_db_path, require_setup


def register_backup_commands(cli):

    @cli.command()
    def backup():
        """
        Backup the vault DB locally and print the path.

        Example:
            vault backup
        """
        require_setup()
        path = backup_db(get_db_path())
        click.echo(f"Backup created at {path}")

    @cli.command("backup_encrypt")
    def backup_encrypt_cmd():
        """
        Backup and encrypt DB with master password.

        Example:
            vault backup_encrypt
        """
        require_setup()
        password = prompt_password()
        path = backup_db(get_db_path())
        encrypted = encrypt_backup(path, password)
        click.echo(f"Encrypted backup created at {encrypted}")

    @cli.command("decrypt_backup")
    @click.argument("encrypted_file", type=click.Path(exists=True))
    @click.option(
        "--output-dir", default=None, help="Optional directory for decrypted DB"
    )
    def decrypt_backup(encrypted_file, output_dir):
        """
        Decrypt an encrypted vault DB backup and restore the original extension.

        Example:
            vault decrypt_backup vault-backups/vault_backup_20251213_123456.db.enc
        """
        require_setup()
        password = prompt_password()
        decrypted_file = decrypt_backup_fn(encrypted_file, password)

        # Restore to original extension if possible
        orig_ext = Path(encrypted_file).stem.split(".")[-1] or ".db"
        decrypted_path = (
            Path(output_dir) / Path(encrypted_file).stem.replace(".enc", "." + orig_ext)
            if output_dir
            else Path(encrypted_file).with_suffix("." + orig_ext)
        )
        decrypted_file.rename(decrypted_path)
        click.echo(f"Decrypted backup written to: {decrypted_path}")
