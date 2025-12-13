import json
from pathlib import Path

from click.testing import CliRunner

from vault.cli import cli


def test_vault_setup_creates_config_and_db(tmp_path, monkeypatch):
    runner = CliRunner()

    # Redirect HOME to temp
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VAULT_CONFIG_DIR", str(tmp_path / ".vault-cli"))

    result = runner.invoke(cli, ["setup"], input="\n\n\n\n")
    assert result.exit_code == 0

    config_path = tmp_path / ".vault-cli" / "config.json"
    assert config_path.exists()

    config = json.loads(config_path.read_text())
    assert "vault_db_path" in config
    assert Path(config["vault_db_path"]).exists()
