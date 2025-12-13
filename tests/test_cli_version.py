import re

from click.testing import CliRunner

from vault.cli import cli


def test_version_flag_shows_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert re.search(r"version \d+\.\d+\.\d+", result.output)
