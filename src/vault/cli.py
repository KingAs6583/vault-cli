import click

from vault import __version__
from vault.commands.backup_commands import register_backup_commands
from vault.commands.config_commands import register_config_commands
from vault.commands.file_commands import register_file_commands
from vault.commands.git_commands import register_git_commands
from vault.commands.setup_commands import register_setup_commands
from vault.commands.text_commands import register_text_commands
from vault.commands.workspace_commands import register_workspace_commands
from vault.config import is_initialized


@click.group(invoke_without_command=True)
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    """Secure Vault CLI"""
    # If no subcommand is provided
    if ctx.invoked_subcommand is None:
        if not is_initialized():
            click.echo("Vault is not initialized.")
            click.echo("Run `vault setup` to continue.")
        else:
            click.echo(ctx.get_help())


@cli.command()
def health():
    """Basic health check"""
    click.echo("Vault CLI is ready.")


register_setup_commands(cli)
register_file_commands(cli)
register_text_commands(cli)
register_backup_commands(cli)
register_git_commands(cli)
register_config_commands(cli)
register_workspace_commands(cli)


if __name__ == "__main__":
    cli()
