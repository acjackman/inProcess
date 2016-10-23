import pytest
from click.testing import CliRunner
from mock import patch

from inprocess import command_line
import os

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_no_settings_file(runner):
    # There is a bug with this test if there is actually an
    # "INPROCESS_SETTINGS" environment variable
    env_vars = {}

    with patch.object(command_line, 'get_app_dir', return_value="inprocess"), \
            runner.isolated_filesystem():
        result = runner.invoke(command_line.cli, ['settings'], env=env_vars)
        print(result.output)
        assert result.exception
        assert result.exit_code == 2

        assert '"inp init"' in result.output.strip()


def test_cli_no_settings_file_with_env_var(runner):
    env_vars = {"INPROCESS_SETTINGS": "settings.json"}

    with patch.object(command_line, 'get_app_dir', return_value="inprocess"), \
            runner.isolated_filesystem():
        result = runner.invoke(command_line.cli, ['settings'], env=env_vars)
        print(result.output)
        assert result.exception
        assert result.exit_code == 2


def test_cli_settings_file(runner):
    app_dir = "inprocess"
    env_vars = {"INPROCESS_SETTINGS": "settings.json"}

    with patch.object(command_line, 'get_app_dir', return_value=app_dir), \
            runner.isolated_filesystem():
        # Start with default configuration
        result = runner.invoke(command_line.cli, ['init'])

        # Check settings file created
        assert os.path.exists(app_dir)
        assert os.path.exists(os.path.join(app_dir, "settings.json"))

        # Move to where env_var says
        os.rename(os.path.join(app_dir, 'settings.json'), 'settings.json')

        result = runner.invoke(command_line.cli, ['settings'], env=env_vars)
        print(result.output)
        assert not result.exception
        assert result.exit_code == 0
