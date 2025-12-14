import subprocess

from click.testing import CliRunner

from vault.cli import cli


def test_workspace_import_and_open(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VAULT_CONFIG_DIR", str(tmp_path / ".vault-cli"))

    runner.invoke(cli, ["setup"], input="\n\n\n\n")

    # Create fake file secret
    jks_file = tmp_path / "test_workspace.jks"
    jks_file.write_bytes(b"workspace-content")

    # Add file (filename is used as key)
    result = runner.invoke(
        cli,
        ["add_file", "myapp", "dev", str(jks_file)],
        input="masterpass\nmasterpass\n",
    )
    assert result.exit_code == 0

    # set workspace path
    workspace_dir = tmp_path / "workspace"
    result = runner.invoke(cli, ["config", "set", "workspace_dir", str(workspace_dir)])
    assert result.exit_code == 0

    # import file into workspace
    result = runner.invoke(
        cli,
        ["workspace", "import", "myapp", "dev", jks_file.name],
        input="masterpass\n",
    )
    assert result.exit_code == 0
    assert (workspace_dir / jks_file.name).exists()

    # mock platform open to avoid actually launching UI
    monkeypatch.setattr(
        subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess(args, 0)
    )
    result = runner.invoke(cli, ["workspace", "open"])
    assert result.exit_code == 0
    assert (
        "Opened workspace" in result.output
        or "Skipping opening workspace in CI environment" in result.output
    )


def test_workspace_open_skips_in_ci(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VAULT_CONFIG_DIR", str(tmp_path / ".vault-cli"))
    runner.invoke(cli, ["setup"], input="\n\n\n\n")
    workspace_dir = tmp_path / "workspace"
    runner.invoke(cli, ["config", "set", "workspace_dir", str(workspace_dir)])
    # Simulate CI environment
    monkeypatch.setenv("CI", "true")
    result = runner.invoke(cli, ["workspace", "open"])
    assert result.exit_code == 0
    assert "Skipping opening workspace in CI environment" in result.output
