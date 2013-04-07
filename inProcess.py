#!/usr/bin/env python
import optparse
import re
import os
import csv
from datetime import datetime
import shutil


class Trackable(object):
    """docstring for Trackable"""
    def __init__(self):
        super(Trackable, self).__init__()
    lines = 1

    def record(self):
        pass

    @classmethod
    def identify(cls, string):
        pass

    @classmethod
    def identify_end(cls, string):
        pass


class Inbox(Trackable):
    """docstring for Inbox"""
    p = re.compile(r"# Inbox")

    lines = 4

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


class Statistic(Trackable):
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
        with open('/Users/Adam/Dropbox/Active/inProcess/Test/Data/' + self.StatName.replace(' ', '')+'.csv', 'ab') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([self.time] + filter(None, self.extras))

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class Task(Trackable):
    """docstring for Task"""
    p = re.compile(r'!- (.*)')

    def __init__(self, string):
        super(Task, self).__init__()
        self.taskstring = self.p.match(string).group(1)

    def record(self):
        os.system("otask '" + self.taskstring + "'")

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class Calendar(Trackable):
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


def main():
    p = optparse.OptionParser()
    p.add_option('--person', '-p', default="world")
    options, arguments = p.parse_args()
    trackables = [Inbox, Statistic, Task, Calendar]

    # Set Variables
    inbox_dir = "/Users/Adam/Dropbox/Active/inProcess/Test/Inbox/"
    inbox_file = "/Users/Adam/Dropbox/Active/inProcess/Test/inbox.md"
    storage_dir = "/Users/Adam/Dropbox/Active/inProcess/Test/LogStorage/"

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
            # Test the single line trackables
            for track in trackables:
                if track.identify(line):
                    if track.lines > 1:
                        lines = []
                        while track.identify_end(line) is None:
                            lines = lines + [line]
                            line = f.readline()
                        track(lines).record()
                    else:
                        track(line).record()
                    break
            else:  # Runs if no track matches
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
