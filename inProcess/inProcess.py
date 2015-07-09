#!/usr/bin/env python
import optparse
import re
import os
from os.path import expanduser
import sys
import csv
from datetime import datetime
import shutil
import json
from parseable import Parseable, Inbox # These are the barebones requirements
from pluginbase import PluginBase


##############################################################################
# Main Loop
##############################################################################

def get_now():
    return datetime.now()

def main(settings_file='~/.inprocess.json', opt_location=False):
    # Redefine Parser
    class MyParser(optparse.OptionParser):
        def format_epilog(self, formatter):
            return self.epilog

    # Parse Command Line options
    parser = MyParser(epilog=(
        '\n(c)2013 Adam Jackman (adam@acjackman.com)\n')
    )
    parser.add_option("-s", "--settings", dest="settings_file",
                      help="set settings file", metavar="FILE")
    parser.add_option('-l', '--location', action="store_true", default=False,
                      help="Print storage locations")
    options, arguments = parser.parse_args()

    # Set Variables
    if options.settings_file is not None:
        settings_file = options.settings_file
    with open(expanduser(settings_file), 'rb') as f:
        settings = json.loads(f.read())
    Parseable.settings = settings  # Pass along settings to the Parseable Class

    if options.location or opt_location:
        print('Storage Locations:\n'
              'Settings:    %s\n'
              'Inbox:       %s\n'
              'inx files:   %s\n'
              'inx storage: %s') % (settings_file, settings['inbox_file'],
                                    settings['inbox_dir'],
                                    settings['storage_dir'])
        sys.exit(0)

    # Import all Parseable classes from parseables folder
    plugin_base = PluginBase(package='parseables')
    plugin_source = plugin_base.make_plugin_source(searchpath=['inProcess/parseables'])
    for plugin_name in plugin_source.list_plugins():
            plugin = plugin_source.load_plugin(plugin_name)

    # List parseable things
    parseables = Parseable.__subclasses__()  # list all direct subclasses of Parseable
    print(parseables)

    # Grab the list of inx files from the inbox directory, plus the inbox file
    files = os.listdir(settings['inbox_dir'])
    fp = re.compile(
        r"inx [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}")
    files = filter(lambda file: fp.match(file), files)
    old_files = [settings['inbox_dir'] + file for file in files]
    new_files = [settings['storage_dir'] + file for file in files]
    now = get_now()
    if os.path.exists(settings['inbox_file']):
        inbox_store = settings['storage_dir'] + "inbox " + now.strftime('%Y-%m-%dT%H-%M-%S') + ".md"
        old_files = [settings['inbox_file']] + old_files
        new_files = [inbox_store] + new_files

    # Setup output
    inbox_header = ("# Inbox\n`inbox.md` created " +
                    now.strftime('%B %d, %Y %H:%M:%S') +
                    "\n\n*" + " *"*29 + "\n\n")
    inbox_contents = ''

    # Loop through the list of files
    for f_index, file in enumerate(old_files):
        with open(file, 'rb') as f:
            line = f.readline()
            while line != '':
                for ident in parseables:
                    if ident.identify(line):
                        if ident.multiline:
                            lines = []
                            record = True
                            while ident.identify_end(line) is None:
                                lines = lines + [line]
                                line = f.readline()
                                if line == '':
                                    inbox_contents = inbox_contents + ''.join(lines) + '\n'
                                    break
                            if record:
                                try:
                                    ident(lines).record()
                                except:
                                    inbox_contents = inbox_contents + ''.join(lines) + '\n'
                        else:
                            try:
                                ident(line).record()
                            except:
                                inbox_contents = inbox_contents + line
                        break
                else:  # Runs if we don't know how to parse the current line
                    inbox_contents = inbox_contents + line
                line = f.readline()
        # After File has been processed:
        # Add blank line to remaining contents
        inbox_contents = inbox_contents + '\n\n'
        # Move the file to storage
        shutil.move(file, new_files[f_index])

    # Log inProcess run
    try:
        with open(settings['data_dir'] + 'log_inProcess.csv', 'ab') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([now])
    except IOError:
        raise RecordError('Problem writing to inProcess log')

    # Write inbox contents to file
    inbox_contents = re.sub(r'\n\s+\n', '\n\n', inbox_contents)  # Change inbox
    if re.sub('\n', '', inbox_contents) != '':
        inbox_contents = inbox_header + inbox_contents
        inbox_contents = re.sub(r"\s*\n\s*\n\s*\n+", r"\n\n", inbox_contents)
        with open(settings['inbox_file'], 'wb') as f:
            f.write(inbox_contents)

if __name__ == '__main__':
    main()
