import click
import os

import json

APP_NAME = "inprocess"


def get_app_dir():
    return click.get_app_dir(APP_NAME, force_posix=True)


def read_settings(settings_file = None):
    # If using custom settings, don't prompt to init
    default_settings = False

    # Default to looking in the App Dir folder
    if settings_file is None:
        default_settings = True
        settings_file = os.path.join(get_app_dir(), 'settings.json')

    try:
        # open file
        if default_settings:
            with click.open_file(settings_file, 'r') as f:
                contents = f.read()
        else:
            contents = settings_file.read()

        settings = json.loads(contents)
    except FileNotFoundError as e:
        # Couldn't find the settings file
        raise click.UsageError('No settings found, run "inp init" to create default settings')

    # Verify Settings by checking that files and directories exist
    # This prevents files from being processed if data can't be written
    return settings


class Config(object):

    def __init__(self):
        self.settings = None


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--settings', '-s', type=click.File(), required=False, envvar='INPROCESS_SETTINGS')
@pass_config
@click.pass_context
def cli(ctx, config, settings):
    """Process and manage short note files."""
    click.echo("CLI executing")
    try:
        config.settings = read_settings(settings)
        click.echo("Read Settings")
    except click.UsageError as e:

        click.echo(ctx.invoked_subcommand)
        if ctx.invoked_subcommand != "init":
            raise e


@cli.command()
@pass_config
def settings(config):
    """Display settings"""
    click.echo("Settings Loaded: %s" % config.settings)

@cli.command()
@pass_config
def init(config):
    """Create default settings"""
    # Application Storage Directory
    app_dir = get_app_dir(APP_NAME, force_posix=True)
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    # Settings file
    default_settings = {
        'inbox': os.path.join(app_dir, 'inbox.yaml'),
        'inx_archive': os.path.join(app_dir, 'inx_archive'),
    }

    with open(os.path.join(app_dir, 'settings.json'), 'w') as f:
        f.write(json.dumps(default_settings))

    # inx archive
    os.makedirs(default_settings['inx_archive'])
