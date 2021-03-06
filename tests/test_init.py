import pytest
from click.testing import CliRunner
from mock import patch
import os

from inprocess import command_line


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_init_creates_defaults(runner):
    app_dir = "inprocess"
    env_vars = {}

    with patch.object(command_line, 'get_app_dir', return_value=app_dir), \
            runner.isolated_filesystem():
        result = runner.invoke(command_line.cli, ['init'], env=env_vars)
        print(result.output)
        assert not result.exception
        assert result.exit_code == 0

        # Check that application directory exists
        assert os.path.exists(app_dir)

        # Check settings file created
        assert os.path.exists(os.path.join(app_dir, "settings.json"))

        # Check inbox_dir created
        assert os.path.exists(os.path.join(app_dir, "inbox_dir"))

        # inx archive folder
        assert os.path.exists(os.path.join(app_dir, "inx_archive"))
        assert os.path.isdir(os.path.join(app_dir, "inx_archive"))

        # parseables folder
        assert os.path.exists(os.path.join(app_dir, "parseables"))
        assert os.path.isdir(os.path.join(app_dir, "parseables"))


def test_cli_init_works_with_env_var(runner):
    app_dir = "inprocess"
    env_vars = {"INPROCESS_SETTINGS": "settings.json"}

    with patch.object(command_line, 'get_app_dir', return_value=app_dir), \
            runner.isolated_filesystem():
        # Start with default configuration
        result = runner.invoke(command_line.cli, ['init'], env=env_vars)
        print(result.output)
        assert not result.exception
        assert result.exit_code == 0

        # Check settings file created
        assert os.path.exists(app_dir)
