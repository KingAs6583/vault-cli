from click.testing import CliRunner
from vault.cli import cli
from pathlib import Path


def test_backup_and_encrypt(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("HOME", str(tmp_path))

    runner.invoke(cli, ["setup"])

    # Backup
    result = runner.invoke(cli, ["backup"])
    assert result.exit_code == 0
    assert "Backup created" in result.output

    # Encrypted backup
    result = runner.invoke(
        cli,
        ["backup_encrypt"],
        input="masterpass\n"
    )
    assert result.exit_code == 0
    assert ".enc" in result.output
