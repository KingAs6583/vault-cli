from datetime import datetime, timezone
from pathlib import Path

import click

from vault.config import get_config_dir, is_initialized, save_config
from vault.storage.db import VaultDB


def register_setup_commands(cli):

    @cli.command()
    def init():
        """Initialize encrypted vault"""
        if not is_initialized():
            if click.confirm("Vault not initialized. Run setup now?", default=True):
                ctx = click.get_current_context()
                ctx.invoke(setup)
        else:
            click.echo("Vault already initialized.")

    @cli.command()
    def setup():
        """First-time setup for Vault CLI"""

        click.echo("Vault CLI - First Time Setup")

        # DB path
        default_db = get_config_dir()
        use_default = click.confirm(
            f"Store vault DB at default location?\n  {default_db}",
            default=True,
        )
        db_path = (
            default_db
            if use_default
            else Path(
                click.prompt(
                    "Directory to store vault DB",
                    type=click.Path(file_okay=False, dir_okay=True),
                )
            )
        )
        db_path = db_path / "vault.db"

        # Backup dir
        backup_dir = Path(
            click.prompt(
                "Backup directory",
                default=str(get_config_dir() / "backups"),
            )
        )

        # Workspace
        enable_workspace = click.confirm(
            "Enable local plaintext workspace for decrypted files?",
            default=False,
        )
        workspace_dir = None
        if enable_workspace:
            workspace_dir = Path(
                click.prompt(
                    "Workspace directory",
                    default=str(get_config_dir() / "workspace"),
                )
            )

        # Git repo (optional)
        git_repo = None
        if click.confirm("Use Git repo for encrypted backups?", default=False):
            git_repo = Path(click.prompt("Path to local Git repo"))

        # Create directories
        db_path.parent.mkdir(parents=True, exist_ok=True)

        click.echo(f"Database will be stored at: {db_path}")

        backup_dir.mkdir(parents=True, exist_ok=True)
        if workspace_dir:
            workspace_dir.mkdir(parents=True, exist_ok=True)

        # Init DB
        VaultDB(str(db_path))
        click.echo("Initialized vault database.")

        save_config(
            {
                "vault_db_path": str(db_path),
                "backup_dir": str(backup_dir),
                "workspace_dir": str(workspace_dir) if workspace_dir else None,
                "git_repo_path": str(git_repo) if git_repo else None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        click.echo("Vault initialized successfully")
