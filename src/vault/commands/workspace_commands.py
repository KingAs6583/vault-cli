import platform
import subprocess
import os
from pathlib import Path

import click

from vault.config import (get_db_path, get_workspace_dir, require_setup,
                          set_config)
from vault.crypto.utils import prompt_password
from vault.storage.db import VaultDB


def register_workspace_commands(cli):

    @cli.group("workspace")
    def workspace_group():
        """Manage the local plaintext workspace for decrypted files."""
        require_setup()

    @workspace_group.command("open")
    def open_workspace():
        """Open the workspace directory in the system file explorer (Windows/ macOS / Linux)."""
        workspace_dir = get_workspace_dir()
        if not workspace_dir:
            if click.confirm(
                "Workspace not configured. Would you like to set it now?", default=False
            ):
                wdir = click.prompt(
                    "Workspace directory",
                    type=click.Path(file_okay=False, dir_okay=True),
                )
                set_config("workspace_dir", str(Path(wdir).resolve()))
                workspace_dir = get_workspace_dir()
            else:
                raise click.ClickException(
                    "Workspace not configured; use `vault setup` or `vault config set workspace_dir <path>` to configure it."
                )
        if not workspace_dir:
            raise click.ClickException(
                "Workspace not configured; use `vault setup` or `vault config set workspace_dir <path>` to configure it."
            )
        p = Path(workspace_dir).resolve()
        p.mkdir(parents=True, exist_ok=True)
        system = platform.system()
        # Avoid attempting to open a GUI file explorer while running in CI
        if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
            click.echo("Skipping opening workspace in CI environment")
            return

        try:
            if system == "Windows":
                os.startfile(str(p))
            elif system == "Darwin":
                subprocess.run(["open", str(p)], check=True)
            else:
                subprocess.run(["xdg-open", str(p)], check=True)
            click.echo(f"Opened workspace: {p}")
        except Exception as e:
            click.echo(f"Failed to open workspace: {e}")

    @workspace_group.command("import")
    @click.argument("project")
    @click.argument("environment")
    @click.argument("file_name")
    def import_file(project: str, environment: str, file_name: str):
        """Decrypt a secret file and copy it into the configured workspace directory."""
        require_setup()
        workspace_dir = get_workspace_dir()
        if not workspace_dir:
            raise click.ClickException(
                "Workspace not configured; use `vault setup` or `vault config set workspace_dir <path>` to configure it."
            )
        # Ensure workspace directory exists
        Path(workspace_dir).mkdir(parents=True, exist_ok=True)
        prompt = prompt_password()
        db = VaultDB(get_db_path())
        temp = db.get_file_secret(
            project, environment, file_name, prompt, workspace_dir
        )
        dest = Path(workspace_dir) / Path(file_name).name
        if dest.exists():
            if not click.confirm(f"File {dest} exists. Overwrite?", default=False):
                db.cleanup_temp_file(str(temp))
                click.echo("Aborted: not copied.")
                return
            else:
                dest.unlink()
        Path(temp).replace(dest)
        click.echo(f"Copied {file_name} to workspace: {dest}")
