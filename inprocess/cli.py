import click
import os

import json

APP_NAME = "InProcess"


def read_settings(settings_file = None):
    # If using custom settings, don't prompt to init
    default_settings = False

    # Default to looking in the App Dir folder
    if settings_file is None:
        default_settings = True
        app_dir = click.get_app_dir(APP_NAME, force_posix=True)
        settings_file = os.path.join(app_dir, 'settings.json')

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
        raise click.UsageError('No settings found, run "in init" to create default settings')

    # Verify Settings by checking that files and directories exist
    # This prevents files from being processed if data can't be written
    return settings

@click.command()
@click.option('--settings', '-s', type=click.File(), required=False, envvar='INPROCESS_SETTINGS')
def main(settings):
    """Process and manage short note files."""
    settings_values = read_settings(settings)
    click.echo("Settings Loaded: %s" % settings_values)
