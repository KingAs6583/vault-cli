from click.testing import CliRunner
from vault.cli import cli
import json


def test_add_and_get_text_secret(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("HOME", str(tmp_path))

    # Setup vault
    runner.invoke(cli, ["setup"])

    # Add secret
    result = runner.invoke(
        cli,
        ["add", "myapp", "dev", "API_KEY", "secret123"],
        input="masterpass\nmasterpass\n"
    )
    assert result.exit_code == 0

    # Get secret
    result = runner.invoke(
        cli,
        ["get", "myapp", "dev", "API_KEY"],
        input="masterpass\n"
    )
    assert "secret123" in result.output
