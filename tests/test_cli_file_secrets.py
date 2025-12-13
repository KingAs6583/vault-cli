from click.testing import CliRunner
from vault.cli import cli
from pathlib import Path


def test_add_and_get_file_secret(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("HOME", str(tmp_path))

    runner.invoke(cli, ["setup"])

    # Create fake .jks file
    jks_file = tmp_path / "test.jks"
    jks_file.write_bytes(b"fake-jks-content")

    # Add file
    result = runner.invoke(
        cli,
        ["add_file", "myapp", "dev", "MY_KEY", str(jks_file)],
        input="masterpass\nmasterpass\n"
    )
    assert result.exit_code == 0

    # Get file
    result = runner.invoke(
        cli,
        ["get_file", "myapp", "dev", "MY_KEY"],
        input="masterpass\n"
    )
    assert "Decrypted file written to" in result.output
