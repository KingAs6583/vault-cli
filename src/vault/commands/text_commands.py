import click
from vault.crypto.utils import prompt_password
from vault.storage.db import VaultDB
from vault.config import get_db_path, require_setup
from vault.exceptions import VaultError


def register_text_commands(cli):

    @cli.command()
    @click.argument("project")
    @click.argument("environment")
    @click.argument("key")
    @click.argument("value")
    def add(project, environment, key, value):
        """
        Add a text secret (API key, password, AdMob ID) to the vault.

        Example:
            vault add myapp dev API_KEY abcd1234
        """
        require_setup()
        try:
            password = prompt_password()
            db = VaultDB(get_db_path())

            # Encrypt value
            salt = db.get_secret(project, environment, key).salt if db.get_secret(project, environment, key) else None
            if not salt:
                from vault.crypto.kdf import generate_salt
                salt = generate_salt()
            from vault.crypto.kdf import derive_key
            from vault.crypto.aes import encrypt
            key_bytes = derive_key(password, salt)
            from datetime import datetime
            iv, ciphertext = encrypt(key_bytes, value.encode("utf-8"))

            from vault.storage.models import SecretRecord
            record = SecretRecord(
                project=project,
                environment=environment,
                key=key,
                value=ciphertext,
                iv=iv,
                salt=salt,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_file=False,
            )
            db.add_secret(record)
            click.echo(f"Text secret {key} added to {project}/{environment}.")
        except VaultError as e:
            click.echo(f"[ERROR] {e}")


    @cli.command()
    @click.argument("project")
    @click.argument("environment")
    @click.argument("key")
    def get(project, environment, key):
        """
        Decrypt and display a text secret safely.

        Example:
            vault get myapp dev API_KEY
        """
        require_setup()
        try:
            password = prompt_password()
            db = VaultDB(get_db_path())
            record = db.get_secret(project, environment, key)
            if not record or record.is_file:
                click.echo(f"No text secret found for {project}/{environment}/{key}")
                return
            from vault.crypto.kdf import derive_key
            from vault.crypto.aes import decrypt
            key_bytes = derive_key(password, record.salt)
            plaintext = decrypt(key_bytes, record.iv, record.value)
            click.echo(f"{key} = {plaintext.decode('utf-8')}")
        except VaultError as e:
            click.echo(f"[ERROR] {e}")


    @cli.command()
    @click.argument("project")
    @click.argument("environment")
    def list(project, environment):
        """
        List all keys stored for a given project and environment.

        Example:
            vault list myapp dev
        """
        require_setup()
        try:
            db = VaultDB(get_db_path())
            cursor = db.conn.execute(
                "SELECT key, is_file FROM secrets WHERE project=? AND environment=?",
                (project, environment),
            )
            rows = cursor.fetchall()
            if not rows:
                click.echo("No secrets found.")
                return
            click.echo(f"Secrets for {project}/{environment}:")
            for key, is_file in rows:
                kind = "File" if is_file else "Text"
                click.echo(f"- {key} ({kind})")
        except VaultError as e:
            click.echo(f"[ERROR] {e}")
