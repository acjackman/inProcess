#!/usr/bin/env python
import optparse
import re
import os
from os.path import expanduser
import sys
from subprocess import Popen, PIPE, STDOUT
import csv
from datetime import datetime
import shutil
import json

##############################################################################
# Parseable Class Definitions
##############################################################################


class RecordError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class Parseable(object):
    """The Parseable superclass"""
    def __init__(self):
        super(Parseable, self).__init__()
    multiline = False
    settings = {"inbox_dir": ".", "inbox_file": ".", "data_dir": ".",
                "storage_dir": "."}

    def record(self):
        pass

    @classmethod
    def identify(cls, string):
        pass

    @classmethod
    def identify_end(cls, string):
        pass

    @classmethod
    def identify_md_hr(cls, string):
        return re.match(r"\s*[\*-]( [\*-]){4,}\s*", string)


class Inbox(Parseable):
    """psudo-parseable to match Inbox heading"""
    p = re.compile(r"# Inbox")
    multiline = True

    def __init__(self):
        super(Inbox, self).__init__()

    def record(self):
        pass

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return cls.identify_md_hr(string)


class CMD(Parseable):
    """psudo-Parseable to match commands"""
    p = re.compile(r"\s*CMD\s+\w+")

    def __init__(self):
        super(CMD, self).__init__()

    def record(self):
        pass

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class Food(Parseable):
    """Food Log parseable"""
    p = re.compile(r'\s*Food ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})')
    multiline = True

    @classmethod
    def breakFLine(cls, string):
        x = string.split('---')
        quanties = ['oz', 'cup', 'cups', 'pack', 'packs', 'slice', 'slices',
                    'piece', 'pieces', 'plate', 'plates', 'bowl', 'bowls']
        q_string = r'|'.join(quanties)
        f_mch = re.match((r"(\s*[-*]\s*)?(([\d/]+)\s*("
                          + q_string +
                          r")?\s+)?(.+)"), x[0])
        # Return tuple is ()
        # Check for comments
        if len(x) == 1:
            return (f_mch.group(3), f_mch.group(4),
                    f_mch.group(5).strip(' \t'), None)
        else:
            return (f_mch.group(3), f_mch.group(4),
                    f_mch.group(5).strip(' \t'),
                    ''.join(x[1:]).strip(' \t'))

    def __init__(self, strings):
        super(Food, self).__init__()
        strings = map(lambda s: s.strip(), strings)
        self.time = self.p.match(strings[0]).group(1)
        # Set items as strings so that you don't modify the originals, in case they need to be checked later
        self.items = strings[1:]

        # Identify and set location
        loc_idx = [i for i, s in enumerate(strings) if re.match('@.*', s)]
        if len(loc_idx) > 0:
            loc_idx = loc_idx.pop()
            self.location = re.match('@\s*(.*)', strings[loc_idx]).group(1)
            self.items.remove(strings[loc_idx])
        else:
            self.location = None

        from_idx = [i for i, s in enumerate(strings) if re.match('>.*', s)]
        if len(from_idx) > 0:
            from_idx = from_idx.pop()
            self.frm = re.match('>\s*(.*)', strings[from_idx]).group(1)
            self.items.remove(strings[from_idx])
            if self.location is None:
                self.location = self.frm
        else:
            self.frm = self.location

        self.items = map(self.breakFLine, self.items)

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'Food.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                for item in self.items:
                    spamwriter.writerow([self.time, self.location, self.frm] + list(item))
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return cls.identify_md_hr(string)


class Journal(Parseable):
    """Add journal entries to Day One"""
    p = re.compile(r'\s*Journal\s+([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})')
    multiline = True

    def __init__(self, strings):
        super(Journal, self).__init__()
        strings = map(lambda s: s.strip(), strings)
        self.time = self.p.match(strings[0]).group(1)
        self.lines = strings[1:]

    def record(self):
        cmd = Popen(['dayone new'], stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=True)
        results = cmd.communicate(input='\n'.join(self.lines))
        if not results[0].startswith('New entry'):
            raise RecordError("Couldn't record journal entry")

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return cls.identify_md_hr(string)


class Statistic(Parseable):
    """Tack statistics that are not otherwise matched"""
    p = re.compile((
        r"\s*([A-z 0-9]+)\. "
        r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})"
        r"(.*)")
    )

    def __init__(self, string):
        super(Statistic, self).__init__()
        m_obj = self.p.match(string)
        self.StatName = m_obj.group(1)
        self.time = m_obj.group(2)
        self.extras = filter(None, m_obj.group(3).split('. '))

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + self.StatName.replace(' ', '')+'.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.time] + self.extras)
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class LifeTrack(Parseable):
    """Parse LifeTrack events"""
    p = re.compile((
        r"\s*Life Track:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})"
        r"\s*---\s*(?=[^\s])(.+)")
    )

    def __init__(self, string):
        super(LifeTrack, self).__init__()
        m_obj = self.p.match(string)
        self.time = m_obj.group(1)
        self.event = m_obj.group(2)

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'LifeTrack.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.time, self.event])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class HealthTrack(Parseable):
    """Parse HealthTrack events"""
    p = re.compile((
        r"\s*Health Track:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})"
        r"\s*---\s*(?=[^\s])(.+)")
    )

    def __init__(self, string):
        super(HealthTrack, self).__init__()
        m_obj = self.p.match(string)
        self.time = m_obj.group(1)
        self.event = m_obj.group(2)

    def record(self):
        data_dir = self.settings['data_dir']
        print data_dir
        try:
            with open(data_dir + 'HealthTrack.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.time, self.event])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class Task(Parseable):
    """Add Tasks to OmniFocus"""
    p = re.compile(r'\s*!-\s*(?=[^\s])(.+)')
    multiline = True

    def __init__(self, strings):
        super(Task, self).__init__()
        self.taskstring = self.p.match(strings[0]).group(1).strip()
        if self.taskstring[-1] == '!':
            self.flagged = True
            self.taskstring = self.taskstring[:-1].strip()
        else:
            self.flagged = False
        self.notes = map(lambda s: s.strip(), strings[1:])

    def record(self):
        if self.notes == []:
            cmd_string = self.taskstring
        else:
            cmd_string = self.taskstring + " (" + '\n'.join(self.notes) + ")"
        if self.flagged:
            cmd_string = cmd_string + ' !'
        cmd = Popen(['otask', cmd_string], stdout=PIPE, stdin=PIPE,
                    stderr=STDOUT, shell=False)
        results = cmd.communicate()
        return results[0].startswith('Task added')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return re.match(r"^$", string)  # Find the next empty line


class Calendar(Parseable):
    """Parse calendar events with Fantastical"""
    p = re.compile(r'\s*!@\s*(?=[^\s])(.+)')

    def __init__(self, string):
        super(Calendar, self).__init__()
        self.eventstring = self.p.match(string).group(1).strip()

    def record(self):
        os.system("osascript -e 'tell application \"Fantastical\""
                  " to parse sentence \"" + self.eventstring +
                  "\" add with immediately'")

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

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
    settings = json.loads(open(expanduser(settings_file), 'rb').read())
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

    # List parseable things
    parseables = Parseable.__subclasses__()  # list all direct subclasses of Parseable

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
                    "\n\n*" + " *"*29 + "\n")
    inbox_contents = ''

    # Loop through the list of files
    for f_index, file in enumerate(old_files):
        f = open(file, 'rb')
        line = f.readline()
        while line != '':
            for ident in parseables:
                if ident.identify(line):
                    if ident.multiline:
                        lines = []
                        while ident.identify_end(line) is None:
                            lines = lines + [line]
                            line = f.readline()
                        try:
                            ident(lines).record()
                        except:
                            inbox_contents = inbox_contents + ''.join(lines)
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
    # Write inbox contents to file
    inbox_contents = re.sub(r'\n\s+\n', '\n\n', inbox_contents)  # Change inbox
    if re.sub('\n', '', inbox_contents) != '':
        f = open(settings['inbox_file'], 'wb')
        inbox_contents = inbox_header + inbox_contents
        inbox_contents = re.sub(r"\s*\n\s*\n\s*\n+", r"\n\n", inbox_contents)
        f.write(inbox_contents)

if __name__ == '__main__':
    main()
