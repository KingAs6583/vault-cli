import json
import os
from pathlib import Path

import click


def get_config_dir() -> Path:
    env_dir = os.environ.get("VAULT_CONFIG_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.home() / ".vault-cli"


def get_config_path() -> Path:
    return get_config_dir() / "config.json"


def get_default_db_path() -> Path:
    return get_config_dir() / "vault.db"


def is_initialized() -> bool:
    path = get_config_path()
    return path.exists() and path.is_file()


def load_config():
    path = get_config_path()
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_config(config: dict):
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2))
    # Best-effort: restrict config file permissions on POSIX
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def get_db_path():
    config = load_config()
    return config.get("vault_db_path", str(get_default_db_path()))


def get_backup_dir() -> str:
    config = load_config()
    return config.get("backup_dir", str(get_config_dir() / "backups"))


def get_workspace_dir() -> str | None:
    config = load_config()
    return config.get("workspace_dir", None)


def get_git_repo_path() -> str | None:
    config = load_config()
    return config.get("git_repo_path", None)


def set_config(key: str, value):
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)


def show_config() -> dict:
    return load_config()


def require_setup():
    if not is_initialized():
        raise click.ClickException("Vault is not initialized. Run `vault setup` first.")
