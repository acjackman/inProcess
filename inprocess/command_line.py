# Python Imports
import os
from os import path
import json
import yaml
import re
from datetime import datetime
import uuid
# Library Imports
import click
from pluginbase import PluginBase

# First-party
from .parseable import Parseable


APP_NAME = "inprocess"


def get_now():
    return datetime.now()


def get_app_dir():
    return click.get_app_dir(APP_NAME, force_posix=True)


class Config(object):
    settings = None
    custom_parseables = None
    parseables = []
    file_prefix = "inx"
    inx_archive = None

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
            with click.open_file(settings_file, 'r') as f:
                contents = f.read()
            settings = json.loads(contents)
        except FileNotFoundError:
            # Couldn't find the settings file
            if default_settings:
                msg = 'No settings found, run "inp init" to create default settings'
            else:
                msg = 'Settings file "%s" does not exist. Aborting.'
            raise click.UsageError(msg)

        # Verify Settings by checking that files and directories exist
        # This prevents files from being processed if data can't be written
        # Required Arguments
        try:
            self.inbox = settings['inbox']
            self.inbox_dir = settings['inbox_dir']
            self.inx_archive = settings['inx_archive']
        except KeyError:
            raise click.Abort("Missing required setting")

        # Optional Arguments
        if 'parseables' in settings and path.isdir(settings['parseables']):
            self.custom_parseables = settings['parseables']

        self.settings = settings


pass_config = click.make_pass_decorator(Config, ensure=True)

CONTEXT_SETTINGS = dict(
    default_map={'process': {}}
)

# @click.group()
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--settings', '-s', type=click.Path(), required=False, envvar='INPROCESS_SETTINGS')
@pass_config
@click.pass_context
def cli(ctx, config, settings):
    """Process and manage short note files."""
    try:
        config.read_settings(settings)
    except click.UsageError as e:
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
        'inbox_dir': path.join(app_dir, 'inbox_dir'),
        'inx_archive': path.join(app_dir, 'inx_archive'),
        'parseables': path.join(app_dir, 'parseables'),
    }

    # make directories
    for dir_key in ['inbox_dir', 'inx_archive', 'parseables']:
        os.makedirs(default_settings[dir_key])

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


@cli.command()
@pass_config
def process(config):
    """process inbox files"""
    now = get_now()

    # Get the new inbox files
    fp = re.compile(r'^' + config.file_prefix + r'.*\.(md|txt)$')
    click.echo(config.inbox_dir)
    click.echo(os.listdir(os.path.join(config.inbox_dir, '')))
    inbox_files = [file for file in os.listdir(config.inbox_dir) if fp.match(file)]
    click.echo(inbox_files)
    # Get the inbox
    try:
        with click.open_file(config.inbox, 'r') as f:
            inbox = yaml.load(f.read())
    except FileNotFoundError:
        # No inbox file is OK, the best inbox zero
        inbox = {
            'processed': None,
            'entries': []
        }

    # Add New files to inbox
    for file_name in inbox_files:
        # Read file to memory
        file_path = path.join(config.inbox_dir, file_name)
        with click.open_file(file_path, 'r') as f:
            entry = {
                'time': os.path.getmtime(file_path),
                'file_name': file_name,
                'id': str(uuid.uuid4()),
                'content': f.read(),
            }
        # Add file to inbox entries
        inbox['entries'].append(entry)

        # Write file to archive
        with click.open_file(path.join(config.inx_archive, entry['id'] + '.yaml'), 'w') as outfile:
            yaml.dump(entry, outfile)

        # Delete file
        os.remove(file_path)

    # Process inbox
    if len(config.parseables) > 0:
        inbox_entries = []  # Unparseable entries go here
        for entry in inbox['entries']:
            # break up into thoughts
            thoughts = entry.content.split(2 * os.linesep)
            inbox_thoughts = []
            for thought in thoughts:
                lines = thought.split(os.linesep)

                # check if the thought is parseable
                for parseable in config.parseables:
                    if parseable.identify(lines[0]):
                        try:
                            parseable(lines).record()
                        except:
                            inbox_thoughts.append(thought)
                        break  # Don't need to check any more parseables, we found the correct one
            # If there were thoughts we couldn't parse, add them to the list of inbox entries
            if len(inbox_thoughts) > 0:
                inbox_entries.append((2 * os.linesep).join(inbox_thoughts))
    else:
        # No parseables available, return all entries
        inbox_entries = inbox['entries']

    # Write new inbox file
    if len(inbox_entries) > 0:
        with click.open_file(config.inbox, 'w') as outfile:
            yaml.dump({
                'processed': now,
                'entries': inbox_entries,
            }, outfile)
