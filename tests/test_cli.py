import pytest
from click.testing import CliRunner
from inprocess import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_no_settings_file(runner):
    # There is a bug with this test if there is actually an
    # "INPROCESS_SETTINGS" environment variable
    env_vars = {}

    with runner.isolated_filesystem():
        result = runner.invoke(cli.main, env = env_vars)
        print(result.output)
        assert result.exception
        assert result.exit_code == 2

        assert '"in init"' in result.output.strip()

def test_cli_no_settings_file_with_env_var(runner):

    env_vars = {"INPROCESS_SETTINGS": "settings.json"}

    with runner.isolated_filesystem():
        result = runner.invoke(cli.main, env = env_vars)
        print(result.output)
        assert result.exception
        assert result.exit_code == 2

def test_cli_settings_file(runner):

    env_vars = {"INPROCESS_SETTINGS": "settings.json"}

    with runner.isolated_filesystem():
        with open('settings.json', 'w') as f:
            f.write('{}')

        result = runner.invoke(cli.main, env = env_vars)
        print(result.output)
        assert not result.exception
        assert result.exit_code == 0
