import subprocess

from click.testing import CliRunner

from vault.cli import cli


def test_git_push_with_config(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("VAULT_CONFIG_DIR", str(tmp_path / ".vault-cli"))

    # Setup vault with default config
    runner.invoke(cli, ["setup"], input="\n\n\n\n")

    # Prepare repo directory and set config
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir(parents=True, exist_ok=True)
    runner.invoke(cli, ["config", "set", "git_repo_path", str(repo_dir)])

    # Monkeypatch subprocess.run to avoid actually invoking git commands
    def fake_run(cmd, cwd=None, check=False):
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    # Run git_push (should not raise and will use fake run)
    result = runner.invoke(cli, ["git_push", "Test commit"], input="masterpass\n")
    assert result.exit_code == 0
    assert "Pushed encrypted backup" in result.output
