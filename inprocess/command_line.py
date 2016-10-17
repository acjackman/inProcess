# Python Imports
import os
from os import path
import json

# Library Imports
import click
from pluginbase import PluginBase

# First-party
from .parseable import Parseable


APP_NAME = "inprocess"


def get_app_dir():
    return click.get_app_dir(APP_NAME, force_posix=True)


class Config(object):
    settings = None
    custom_parseables = None
    parseables = []

    def __init__(self):
        pass

    def read_settings(self, settings_file=None):
        # If using custom settings, don't prompt to init
        default_settings = False

        # Default to looking in the App Dir folder
        if settings_file is None:
            default_settings = True
            settings_file = path.join(get_app_dir(), 'settings.json')

        try:
            # open file
            if default_settings:
                with click.open_file(settings_file, 'r') as f:
                    contents = f.read()
            else:
                contents = settings_file.read()

            settings = json.loads(contents)
        except FileNotFoundError:
            # Couldn't find the settings file
            raise click.UsageError('No settings found, run "inp init" to create default settings')

        # Verify Settings by checking that files and directories exist
        # This prevents files from being processed if data can't be written
        if 'parseables' in settings and path.isdir(settings['parseables']):
            self.custom_parseables = settings['parseables']
        self.settings = settings


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--settings', '-s', type=click.File(), required=False, envvar='INPROCESS_SETTINGS')
@pass_config
@click.pass_context
def cli(ctx, config, settings):
    """Process and manage short note files."""
    click.echo("CLI executing")
    try:
        config.read_settings(settings)
        click.echo("Read Settings")
    except click.UsageError as e:

        click.echo(ctx.invoked_subcommand)
        if ctx.invoked_subcommand != "init":
            raise e

    # Load all available Parseables
    plugin_base = PluginBase(package='parseables')
    project_dir = path.dirname(path.dirname(path.abspath(__file__)))
    parsables_dir = path.join(project_dir, 'parseables', '')  # adding '' makes a trailing slash
    plugin_source = plugin_base.make_plugin_source(searchpath=[
        # Places to look for parseables:
        parsables_dir,  # built in parseables
        config.custom_parseables  # User-added
    ])
    try:
        for plugin_name in plugin_source.list_plugins():
            plugin_source.load_plugin(plugin_name)
            pass
    except TypeError:
        # No parseable plug-ins are available
        pass

    config.parseables = Parseable.__subclasses__()


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
    if not path.exists(app_dir):
        os.makedirs(app_dir)

    default_settings = {
        'inbox': path.join(app_dir, 'inbox.yaml'),
        'inx_archive': path.join(app_dir, 'inx_archive'),
        'parseables': path.join(app_dir, 'parseables'),
    }

    # inx archive
    os.makedirs(default_settings['inx_archive'])

    # parseables plugin dir
    os.makedirs(default_settings['parseables'])

    # create settings file
    with open(path.join(app_dir, 'settings.json'), 'w') as f:
        f.write(json.dumps(default_settings))


@cli.command()
@pass_config
def inbox(config):
    """open inbox.yaml in a text editor"""
    click.edit(config.settings['inbox'])


@cli.command()
@pass_config
def parseables(config):
    """List of parseables and their status"""
    if len(config.parseables) == 0:
        click.echo('No Parseables are available, add some to "%s"' % config.custom_parseables)
    else:
        click.echo("Available Parseables:")
        for parseable in config.parseables:
            click.echo("- %s" % parseable.__name__)
