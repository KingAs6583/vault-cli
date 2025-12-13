import json
from pathlib import Path

import click

CONFIG_DIR = Path.home() / ".vault-cli"
CONFIG_PATH = CONFIG_DIR / "config.json"
DEFAULT_DB_PATH = "project-metadata/data/vault.db"


def is_initialized() -> bool:
    return CONFIG_PATH.exists() and CONFIG_PATH.is_file()

def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))


def get_db_path():
    config = load_config()
    return config.get("vault_db_path", DEFAULT_DB_PATH)

def require_setup():
    if not is_initialized():
        raise click.ClickException(
            "Vault is not initialized. Run `vault setup` first."
        )