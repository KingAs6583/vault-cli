import click

from vault.config import set_config, show_config


def register_config_commands(cli):

    @cli.group("config")
    def config_group():
        """View and modify vault configuration."""
        # Config commands available even before setup.

    @config_group.command("show")
    def show():
        cfg = show_config()
        click.echo(format_json(cfg))

    @config_group.command("set")
    @click.argument("key")
    @click.argument("value")
    def set_cmd(key: str, value: str):
        set_config(key, value)
        click.echo(f"Updated {key} to {value}")


def format_json(obj: dict) -> str:
    import json

    return json.dumps(obj, indent=2)
