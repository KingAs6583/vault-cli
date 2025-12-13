import click
import subprocess
from vault.crypto.utils import prompt_password
from vault.storage.backup import encrypt_backup
from vault.config import get_db_path, require_setup


def register_git_commands(cli):

    @cli.command("git_push")
    @click.argument("message", default="Vault encrypted backup")
    def git_push(commit_message: str):
        """
        Encrypt the vault DB and push to remote Git repo.

        Example:
            vault git_push "Daily encrypted backup"
        """
        require_setup()
        try:
            password = prompt_password()
            db_path = get_db_path()
            encrypted_file = encrypt_backup(db_path, password)

            # Git commands
            subprocess.run(["git", "add", str(encrypted_file)], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            subprocess.run(["git", "push"], check=True)

            click.echo(f"Pushed encrypted backup to remote repo: {encrypted_file}")
        except subprocess.CalledProcessError as e:
            click.echo(f"[ERROR] Git push failed: {e}")
        except Exception as e:
            click.echo(f"[ERROR] {e}")

