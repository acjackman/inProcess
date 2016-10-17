import pytest
from click.testing import CliRunner
from unittest.mock import patch
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

        # inx archive folder
        assert os.path.exists(os.path.join(app_dir, "inx_archive"))
        assert os.path.isdir(os.path.join(app_dir, "inx_archive"))

        # parseables folder
        assert os.path.exists(os.path.join(app_dir, "parseables"))
        assert os.path.isdir(os.path.join(app_dir, "parseables"))
