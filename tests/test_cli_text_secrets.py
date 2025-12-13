from click.testing import CliRunner

from vault.cli import cli


def test_add_and_get_text_secret(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VAULT_CONFIG_DIR", str(tmp_path / ".vault-cli"))

    # Setup vault
    runner.invoke(cli, ["setup"], input="\n\n\n\n")

    # Add secret (master password, then secret + confirm)
    result = runner.invoke(
        cli,
        ["add", "myapp", "dev", "API_KEY"],
        input="masterpass\nsecret123\nsecret123\n",
    )
    assert result.exit_code == 0

    # Get secret (use --show to reveal secret)
    result = runner.invoke(
        cli, ["get", "myapp", "dev", "API_KEY", "--show"], input="masterpass\n"
    )
    assert "secret123" in result.output
