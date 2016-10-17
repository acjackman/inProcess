import pytest
from click.testing import CliRunner
from unittest.mock import patch

from inprocess import command_line


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_empty_parseables_list(runner):
    env_vars = {}

    with patch.object(command_line, 'get_app_dir', return_value="inprocess"), \
            patch.object(command_line.Config, 'parseables', return_value=[]), \
            runner.isolated_filesystem():
        runner.invoke(command_line.cli, ['init'], env=env_vars)

        # Check that the file is opened
        result = runner.invoke(command_line.cli, ['parseables'], env=env_vars)
        print(result.output)
        assert not result.exception
        assert result.exit_code == 0
        assert 'No Parseables are available' in result.output.strip()


@pytest.mark.skip(reason="Need to write Parseables first")
def test_cli_parseables_list(runner):
    env_vars = {}

    with patch.object(command_line, 'get_app_dir', return_value="inprocess"), \
            patch.object(command_line.Config, 'parseables', return_value=[]), \
            runner.isolated_filesystem():
        runner.invoke(command_line.cli, ['init'], env=env_vars)

        # Check that the file is opened
        result = runner.invoke(command_line.cli, ['parseables'], env=env_vars)
        print(result.output)
        assert not result.exception
        assert result.exit_code == 0
        assert 'Available Parseables:' in result.output.strip()
