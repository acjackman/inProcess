#!/usr/bin/env python
import optparse
import re
import os
from os.path import expanduser
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
        pass

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return re.match(r"([\*-] ){4,}", string)


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

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class LifeTrack(Parseable):
    """docstring for Statistic"""
    p = re.compile((
        r"Life Track: ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}) ---"
        r"(.*)")
    )

    def __init__(self, string):
        super(Statistic, self).__init__()
        m_obj = self.p.match(string)
        self.time = m_obj.group(1)
        self.Event = m_obj.group(2)

    def record(self):
        data_dir = self.settings['data_dir']
        with open(data_dir + 'LifeTrack.csv', 'ab') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([self.time, self.Event])

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class HealthTrack(Parseable):
    """docstring for Statistic"""
    p = re.compile((
        r"Health Track: ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}) ---"
        r"(.*)")
    )

    def __init__(self, string):
        super(Statistic, self).__init__()
        m_obj = self.p.match(string)
        self.time = m_obj.group(1)
        self.Event = m_obj.group(2)

    def record(self):
        data_dir = self.settings['data_dir']
        with open(data_dir + 'HealthTrack.csv', 'ab') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([self.time, self.Event])

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class Task(Parseable):
    """docstring for Task"""
    p = re.compile(r'!- (.*)')
    multiline = True

    def __init__(self, strings):
        super(Task, self).__init__()
        self.taskstring = self.p.match(strings[0]).group(1)
        self.notes = map(lambda s: s.strip(), strings[1:])

    def record(self):
        if self.notes == []:
            os.system("otask '" + self.taskstring + "'" + "> /dev/null 2>&1")
        else:
            os.system("otask '" + self.taskstring + " (" + '\n'.join(self.notes) + ")'" + "> /dev/null 2>&1")

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
        os.system("osascript -e 'tell application \"Fantastical\" to parse sentence \"" + self.eventstring + "\" with add immediately'")

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
    trackables = [Statistic, Task, Calendar, LifeTrack, HealthTrack, Inbox]

    # Grab the list of inx files from the inbox directory, plus the inbox file
    files = os.listdir(inbox_dir)
    fp = re.compile(
        r"inx [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}")
    files = filter(lambda file: fp.match(file), files)
    old_files = [inbox_file] + [inbox_dir + file for file in files]
    now = datetime.now()
    inbox_store = storage_dir + "inbox " + now.strftime('%Y-%m-%dT%H-%M-%S') + ".md"
    new_files = [inbox_store] + [storage_dir + file for file in files]

    # Setup output
    inbox_header = "# Inbox\n`inbox.md` created " + now.strftime('%B %d, %Y %H:%M:%S') + "\n\n* * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n"
    inbox_contents = ''

    # Loop through the list of files
    for f_index, file in enumerate(old_files):
        f = open(file, 'rb')
        line = f.readline()
        while line != '':
            for track in trackables:
                if track.identify(line):
                    if track.multiline:
                        lines = []
                        while track.identify_end(line) is None:
                            lines = lines + [line]
                            line = f.readline()
                        track(lines).record()
                    else:
                        track(line).record()
                    break
            else:  # Runs if we don't know how to parse the current line
                inbox_contents = inbox_contents + line
            line = f.readline()
        # Move the file that has been read to storage
        shutil.move(file, new_files[f_index])
    # Write inbox contents to file
    if inbox_contents != '':
        f = open(inbox_file, 'wb')
        inbox_contents = inbox_header + inbox_contents
        inbox_contents = re.sub(r"\n\n\n+", r"\n\n", inbox_contents)
        f.write(inbox_contents)

if __name__ == '__main__':
    main()
