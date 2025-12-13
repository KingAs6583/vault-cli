
from click.testing import CliRunner

from vault.cli import cli


def test_add_and_get_file_secret(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VAULT_CONFIG_DIR", str(tmp_path / ".vault-cli"))

    runner.invoke(cli, ["setup"], input="\n\n\n\n")

    # Create fake .jks file
    jks_file = tmp_path / "test.jks"
    jks_file.write_bytes(b"fake-jks-content")

    # Add file (filename is used as key)
    result = runner.invoke(
        cli,
        ["add_file", "myapp", "dev", str(jks_file)],
        input="masterpass\nmasterpass\n",
    )
    assert result.exit_code == 0

    # Get file by filename (key is filename including extension)
    filename_key = jks_file.name
    result = runner.invoke(
        cli, ["get_file", "myapp", "dev", filename_key], input="masterpass\n"
    )
    assert "Decrypted file written to" in result.output

    # Get file and copy to workspace
    # Configure workspace path
    workspace_dir = tmp_path / "workspace"
    runner.invoke(cli, ["config", "set", "workspace_dir", str(workspace_dir)])
    result = runner.invoke(
        cli,
        ["get_file", "myapp", "dev", filename_key, "--to-workspace"],
        input="masterpass\n",
    )
    assert result.exit_code == 0
    assert "Decrypted file copied to workspace" in result.output
    assert (workspace_dir / filename_key).exists()
