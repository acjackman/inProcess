import pytest
from click.testing import CliRunner
from unittest.mock import patch

from inprocess import command_line


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_settings_file(runner):
    env_vars = {}

    with patch.object(command_line, 'get_app_dir', return_value="inprocess"), \
            runner.isolated_filesystem():
        result = runner.invoke(command_line.cli, ['init'], env = env_vars)
        print(result.output)
        assert not result.exception
        assert result.exit_code == 0
