
from click.testing import CliRunner

from vault.cli import cli


def test_backup_and_encrypt(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VAULT_CONFIG_DIR", str(tmp_path / ".vault-cli"))

    runner.invoke(cli, ["setup"], input="\n\n\n\n")

    # Backup
    result = runner.invoke(cli, ["backup"])
    assert result.exit_code == 0
    assert "Backup created" in result.output

    # Encrypted backup
    result = runner.invoke(cli, ["backup_encrypt"], input="masterpass\n")
    assert result.exit_code == 0
    assert ".enc" in result.output


def test_config_set_and_show(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    # setup
    runner.invoke(cli, ["setup"], input="\n\n\n\n")

    # set git_repo_path
    repo_path = str(tmp_path / "myrepo")
    result = runner.invoke(cli, ["config", "set", "git_repo_path", repo_path])
    assert result.exit_code == 0
    assert "Updated git_repo_path" in result.output

    # show config contains the new value (parse JSON output)
    result = runner.invoke(cli, ["config", "show"])
    assert result.exit_code == 0
    import json

    cfg = json.loads(result.output)
    assert cfg.get("git_repo_path") == repo_path
