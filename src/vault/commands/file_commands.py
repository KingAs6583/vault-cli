from pathlib import Path

import click

from vault.config import get_db_path, require_setup
from vault.crypto.utils import prompt_password
from vault.storage.db import VaultDB


def register_file_commands(cli):

    @cli.command("add_file")
    @click.argument("project")
    @click.argument("environment")
    @click.argument("file", type=click.Path(exists=True))
    def add_file(project: str, environment: str, file: str):
        """
        Encrypt a file (.jks, .pem, etc.) and store it in vault.

        Using filename as the key automatically (including extension). Example:
            vault add_file myapp dev ./generalkey.jks
        """
        require_setup()
        password = prompt_password(confirm=True)
        db = VaultDB(get_db_path())
        key = Path(file).name
        db.add_file_secret(project, environment, key, file, password)
        click.echo(f"File secret {key} added.")

    @cli.command("get_file")
    @click.argument("project")
    @click.argument("environment")
    @click.argument("file_name")
    @click.option("--output-dir", default=None, help="Optional output directory")
    @click.option(
        "--to-workspace",
        is_flag=True,
        default=False,
        help="Copy decrypted file into configured workspace directory",
    )
    def get_file(
        project: str,
        environment: str,
        file_name: str,
        output_dir: str,
        to_workspace: bool,
    ):
        """
        Decrypt a file secret and write it to a temporary file.

        Use the original filename (including extension) as the key. Example:
            vault get_file myapp dev generalkey.jks
        """
        require_setup()
        password = prompt_password()
        db = VaultDB(get_db_path())
        # file_name is the key used when storing the file (basename with extension)
        # If user requests to copy to workspace, ensure workspace is configured
        workspace_dir = None
        if to_workspace:
            from vault.config import get_workspace_dir, set_config

            workspace_dir = get_workspace_dir()
            if not workspace_dir:
                if click.confirm(
                    "Workspace not configured. Do you want to set it now?",
                    default=False,
                ):
                    wdir = click.prompt(
                        "Workspace directory",
                        type=click.Path(file_okay=False, dir_okay=True),
                    )
                    set_config("workspace_dir", str(Path(wdir).resolve()))
                    workspace_dir = get_workspace_dir()
                else:
                    raise click.ClickException(
                        "Workspace not configured; run `vault setup` or "
                        "`vault config set workspace_dir <path>` to configure it."
                    )
            if workspace_dir:
                Path(workspace_dir).mkdir(parents=True, exist_ok=True)

        temp_path = db.get_file_secret(
            project,
            environment,
            file_name,
            password,
            output_dir if not to_workspace else workspace_dir,
        )

        if to_workspace and workspace_dir:
            # Move temp to final name in workspace, overwrite if confirmed
            dest = Path(workspace_dir) / Path(file_name).name
            if dest.exists():
                if not click.confirm(
                    f"File {dest} already exists in workspace. Overwrite?",
                    default=False,
                ):
                    db.cleanup_temp_file(str(temp_path))
                    click.echo("Aborted: file not copied to workspace.")
                    return
                else:
                    dest.unlink()
            Path(temp_path).replace(dest)
            click.echo(f"Decrypted file copied to workspace: {dest}")
        else:
            click.echo(f"Decrypted file written to {temp_path}")
