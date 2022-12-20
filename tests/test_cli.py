from typer.testing import CliRunner

from sparql_profiler.__main__ import cli

runner = CliRunner()


def test_cli():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
