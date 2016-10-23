import pytest
from click.testing import CliRunner
from mock import patch
import click


from inprocess import command_line


@pytest.fixture
def runner():
    return CliRunner()


@patch.object(click, 'edit')
def test_cli_opens_inbox(mock, runner):
    app_dir = "inprocess"
    env_vars = {}

    with patch.object(command_line, 'get_app_dir', return_value=app_dir), \
            runner.isolated_filesystem():
        # Initialize the environment
        runner.invoke(command_line.cli, ['init'], env=env_vars)

        # Check that the file is opened
        result = runner.invoke(command_line.cli, ['inbox'], env=env_vars)
        print(result.output)
        assert not result.exception
        assert result.exit_code == 0
        assert mock.called is True
