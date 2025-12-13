import click

from vault.config import get_db_path, require_setup
from vault.crypto.utils import prompt_password
from vault.exceptions import VaultError
from vault.storage.db import VaultDB


def register_text_commands(cli):

    @cli.command()
    @click.argument("project")
    @click.argument("environment")
    @click.argument("key")
    def add(project, environment, key):
        """
        Add a text secret (API key, password, AdMob ID) to the vault.

        Example:
            vault add myapp dev API_KEY
        """
        require_setup()
        try:
            password = prompt_password()
            # Prompt for secret value to avoid placing secrets on command line
            value = click.prompt(
                "Secret value", hide_input=True, confirmation_prompt=True
            )
            db = VaultDB(get_db_path())

            # Encrypt value
            existing = db.get_secret(project, environment, key)
            salt = existing.salt if existing else None
            if not salt:
                from vault.crypto.kdf import generate_salt

                salt = generate_salt()
            from vault.crypto.aes import encrypt
            from vault.crypto.kdf import derive_key

            key_bytes = derive_key(password, salt)
            from datetime import datetime, timezone

            iv, ciphertext = encrypt(key_bytes, value.encode("utf-8"))

            from vault.storage.models import SecretRecord

            record = SecretRecord(
                project=project,
                environment=environment,
                key=key,
                value=ciphertext,
                iv=iv,
                salt=salt,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
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
    @click.option(
        "--show",
        is_flag=True,
        default=False,
        help="Show secret value (this may display sensitive data)",
    )
    def get(project, environment, key, show):
        """
        Decrypt and display a text secret safely. Use --show to print the secret value.

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
            from vault.crypto.aes import decrypt
            from vault.crypto.kdf import derive_key

            key_bytes = derive_key(password, record.salt)
            plaintext = decrypt(key_bytes, record.iv, record.value)
            if show:
                click.echo(f"{key} = {plaintext.decode('utf-8')}")
            else:
                click.echo(f"{key} = **** (hidden). Use --show to reveal")
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
