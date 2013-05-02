#!/usr/bin/env python
import optparse
import re
import os
from os.path import expanduser
from subprocess import Popen, PIPE, STDOUT
import csv
from datetime import datetime
import shutil
import json

##############################################################################
# Parseable Class Definitions
##############################################################################


class Parseable(object):
    """docstring for Parseable"""
    def __init__(self):
        super(Parseable, self).__init__()
    multiline = False
    settings = json.loads(open(expanduser('~/.inprocess.json'), 'rb').read())

    def record(self):
        pass

    @classmethod
    def identify(cls, string):
        pass

    @classmethod
    def identify_end(cls, string):
        pass


class Inbox(Parseable):
    """docstring for Inbox"""
    p = re.compile(r"# Inbox")
    multiline = True

    def __init__(self, arg):
        super(Inbox, self).__init__()
        self.arg = arg

    def record(self):
        return True

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return re.match(r"([\*-] ){4,}", string)


class CMD(Parseable):
    """docstring for Command Lines"""
    p = re.compile(r"\s*CMD.+")

    def __init__(self, arg):
        super(CMD, self).__init__()
        self.arg = arg

    def record(self):
        return True

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class Food(Parseable):
    """docstring for Food"""
    p = re.compile(r'Food ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})')
    multiline = True

    def __init__(self, strings):
        super(Food, self).__init__()
        strings = map(lambda s: s.strip(), strings)
        self.time = self.p.match(strings[0]).group(1)
        self.items = strings[1:]
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
        else:
            self.frm = self.location

        def breakFLine(string):
            x = string.split('---')
            f_mch = re.match((r"([*-+]\s*)?"
                              r'(([\d/]+)\s*(oz|cup|cups|pack|packs|slice|slices|piece|pieces|plate|plates|bowl|bowls)?\s+)?'
                              r"(.+)"), x[0])
            if len(x) == 1:
                return (f_mch.group(3), f_mch.group(4),
                        f_mch.group(5).strip(' \t'), None)
            else:
                return (f_mch.group(3), f_mch.group(4),
                        f_mch.group(5).strip(' \t'),
                        ''.join(x[1:]).strip(' \t'))

        self.items = map(breakFLine, self.items)

    def record(self):
        data_dir = self.settings['data_dir']
        with open(data_dir + 'Food.csv', 'ab') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            for item in self.items:
                spamwriter.writerow([self.time, self.location, self.frm] + list(item))
        return True

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return re.match(r"([\*-] ){5,}", string)


class Journal(Parseable):
    """docstring for Journal"""
    p = re.compile(r'Journal ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})')
    multiline = True

    def __init__(self, strings):
        super(Journal, self).__init__()
        strings = map(lambda s: s.strip(), strings)
        self.time = self.p.match(strings[0]).group(1)
        self.lines = strings[1:]

    def record(self):
        cmd = Popen(['dayone new'], stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=True)
        results = cmd.communicate(input='\n'.join(self.lines))
        return results[0].startswith('New entry')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return re.match(r"([\*-] ){5,}", string)


class Statistic(Parseable):
    """docstring for Statistic"""
    p = re.compile((
        r"([A-z 0-9]+)\. "
        r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})"
        r"(.*)")
    )

    def __init__(self, string):
        super(Statistic, self).__init__()
        m_obj = self.p.match(string)
        self.StatName = m_obj.group(1)
        self.time = m_obj.group(2)
        self.extras = m_obj.group(3).split('. ')

    def record(self):
        data_dir = self.settings['data_dir']
        with open(data_dir + self.StatName.replace(' ', '')+'.csv', 'ab') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([self.time] + filter(None, self.extras))
        return True

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class LifeTrack(Parseable):
    """docstring for LifeTrack"""
    p = re.compile((
        r"Life Track: ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}) ---"
        r"\s*(.*)")
    )

    def __init__(self, string):
        super(LifeTrack, self).__init__()
        m_obj = self.p.match(string)
        self.time = m_obj.group(1)
        self.Event = m_obj.group(2)

    def record(self):
        data_dir = self.settings['data_dir']
        with open(data_dir + 'LifeTrack.csv', 'ab') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([self.time, self.Event])
        return True

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class HealthTrack(Parseable):
    """docstring for HealthTrack"""
    p = re.compile((
        r"Health Track: ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}) ---"
        r"\s*(.*)")
    )

    def __init__(self, string):
        super(HealthTrack, self).__init__()
        m_obj = self.p.match(string)
        self.time = m_obj.group(1)
        self.Event = m_obj.group(2)

    def record(self):
        data_dir = self.settings['data_dir']
        with open(data_dir + 'HealthTrack.csv', 'ab') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([self.time, self.Event])
        return True

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class Task(Parseable):
    """docstring for Task"""
    p = re.compile(r'!- (.*) (!)?')
    multiline = True

    def __init__(self, strings):
        super(Task, self).__init__()
        self.taskstring = self.p.match(strings[0]).group(1)
        if self.p.match(strings[0]).group(2):
            self.flagged = True
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
    """docstring for Calendar"""
    p = re.compile(r'!@ (.*)')

    def __init__(self, string):
        super(Calendar, self).__init__()
        self.eventstring = self.p.match(string).group(1)

    def record(self):
        os.system("osascript -e 'tell application \"Fantastical\""
                  " to parse sentence \"" + self.eventstring +
                  "\" add with immediately'")
        return True

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

##############################################################################
# Main Loop
##############################################################################


def main():
    # Set Variables
    settings = json.loads(open(expanduser('~/.inprocess.json'), 'rb').read())
    inbox_dir = settings['inbox_dir']
    inbox_file = settings['inbox_file']
    storage_dir = settings['storage_dir']

    # Redefine Parser
    class MyParser(optparse.OptionParser):
        def format_epilog(self, formatter):
            return self.epilog

    # Parse Command Line options
    p = MyParser(epilog=(
        '\nStorage Locations:\n'
        'Inbox: %s\n'
        'inx files: %s\n'
        'inx storage: %s\n') % (inbox_file, inbox_dir, storage_dir)
    )
    options, arguments = p.parse_args()

    # List parseable things
    parseables = [Statistic, Task, Food, Calendar, Journal,
                  LifeTrack, HealthTrack, CMD, Inbox]

    # Grab the list of inx files from the inbox directory, plus the inbox file
    files = os.listdir(inbox_dir)
    fp = re.compile(
        r"inx [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}")
    files = filter(lambda file: fp.match(file), files)
    old_files = [inbox_dir + file for file in files]
    new_files = [storage_dir + file for file in files]
    now = datetime.now()
    if os.path.exists(inbox_file):
        inbox_store = storage_dir + "inbox " + now.strftime('%Y-%m-%dT%H-%M-%S') + ".md"
        old_files = [inbox_file] + old_files
        new_files = [inbox_store] + new_files

    # Setup output
    inbox_header = ("# Inbox\n`inbox.md` created " +
                    now.strftime('%B %d, %Y %H:%M:%S') +
                    "\n\n* * * * * * * * * * * * * * * * *"
                    " * * * * * * * * * * * * *\n")
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
                        if not ident(lines).record():
                            inbox_contents = inbox_contents + ''.join(lines)
                    else:
                        if not ident(line).record():
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
    if re.sub('\n', '', inbox_contents) != '':
        f = open(inbox_file, 'wb')
        inbox_contents = inbox_header + inbox_contents
        inbox_contents = re.sub(r"\n\n\n+", r"\n\n", inbox_contents)
        f.write(inbox_contents)

if __name__ == '__main__':
    main()
