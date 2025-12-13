import click
from vault.crypto.utils import prompt_password
from vault.storage.db import VaultDB
from vault.config import get_db_path, require_setup


def register_file_commands(cli):

    @cli.command("add_file")
    @click.argument("project")
    @click.argument("environment")
    @click.argument("key")
    @click.argument("file", type=click.Path(exists=True))
    def add_file(project: str, environment: str, key: str, file: str):
        """
        Encrypt a file (.jks, .pem, etc.) and store it in vault.

        Example:
            vault add_file myapp dev MY_KEY ./generalkey.jks
        """
        require_setup()
        password = prompt_password(confirm=True)
        db = VaultDB(get_db_path())
        db.add_file_secret(project, environment, key, file, password)
        click.echo(f"File secret {key} added.")

    @cli.command("get_file")
    @click.argument("project")
    @click.argument("environment")
    @click.argument("key")
    @click.option("--output-dir", default=None, help="Optional output directory")
    def get_file(project: str, environment: str, key: str, output_dir: str):
        """
        Decrypt a file secret and write it to a temporary file.

        Example:
            vault get_file myapp dev MY_KEY
        """
        require_setup()
        password = prompt_password()
        db = VaultDB(get_db_path())
        path = db.get_file_secret(project, environment, key, password, output_dir)
        click.echo(f"Decrypted file written to {path}")
