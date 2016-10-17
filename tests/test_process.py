import pytest
from click.testing import CliRunner
from unittest.mock import patch
import os

from inprocess import command_line


@pytest.fixture
def runner():
    return CliRunner()


# @pytest.mark.skip(reason="Need to write Parseables first")
def test_cli_process_single_file(runner):
    app_dir = "inprocess"
    env_vars = {}

    with patch.object(command_line, 'get_app_dir', return_value=app_dir), \
            runner.isolated_filesystem():
        # Initialize Environment
        runner.invoke(command_line.cli, ['init'], env=env_vars)

        # Make Notes Directory with a single inx file inside
        notes_dir = 'Notes'
        os.makedirs(notes_dir)

        with open(os.path.join(app_dir, 'inbox_dir', 'inx.md'), 'w') as f:
            f.write('A thought')

        # Run inprocess
        result = runner.invoke(command_line.cli, ['process'], env=env_vars)
        print(result.output)
        assert not result.exception
        assert result.exit_code == 0

        # File is moved to archive
        archive_dir = os.path.join(app_dir, 'inx_archive')
        num_files_in_archive = len([name for name in os.listdir(archive_dir)
                                    if os.path.isfile(os.path.join(archive_dir, name))])
        assert num_files_in_archive == 1

        # inbox.yaml is created
        assert os.path.exists(os.path.join(app_dir, "inbox.yaml"))
