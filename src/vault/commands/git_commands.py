import subprocess
from pathlib import Path

import click

from vault.config import (
    get_backup_dir,
    get_db_path,
    get_git_repo_path,
    require_setup,
    set_config,
)
from vault.crypto.utils import prompt_password
from vault.storage.backup import backup_db, encrypt_backup


def register_git_commands(cli):

    @cli.command("git_push")
    @click.argument("message", default="Vault encrypted backup")
    def git_push(message: str):
        """
        Encrypt the vault DB and push to remote Git repo.

        Example:
            vault git_push "Daily encrypted backup"
        """
        require_setup()
        try:
            password = prompt_password()
            repo = get_git_repo_path()
            if not repo:
                if click.confirm(
                    "No Git repo configured. Set git_repo_path now?", default=False
                ):
                    repo_path = click.prompt(
                        "Path to local Git repo",
                        type=click.Path(file_okay=False, dir_okay=True),
                    )
                    set_config("git_repo_path", str(Path(repo_path).resolve()))
                    repo = get_git_repo_path()
                else:
                    raise click.ClickException(
                        "No git repo configured; run `vault config set git_repo_path <path>` to configure it."
                    )

            # Create a backup in backup_dir and encrypt
            backup_path = backup_db(get_db_path(), backup_dir=get_backup_dir())
            encrypted_file = encrypt_backup(backup_path, password)

            # Copy encrypted file into repo and git add/commit/push
            if repo:
                repo_path = Path(repo)
            else:
                repo_path = None
            if not repo_path or not repo_path.exists():
                raise click.ClickException(
                    f"Configured git repo path not found: {repo}"
                )
            # move the encrypted file into repo
            dest = repo_path / encrypted_file.name
            encrypted_file.replace(dest)

            subprocess.run(["git", "add", str(dest)], cwd=str(repo_path), check=True)
            subprocess.run(
                ["git", "commit", "-m", message], cwd=str(repo_path), check=True
            )
            subprocess.run(["git", "push"], cwd=str(repo_path), check=True)

            click.echo(f"Pushed encrypted backup to remote repo: {dest}")
        except subprocess.CalledProcessError as e:
            click.echo(f"[ERROR] Git push failed: {e}")
        except Exception as e:
            click.echo(f"[ERROR] {e}")
