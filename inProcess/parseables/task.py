from parseable import Parseable
import re
from subprocess import Popen, PIPE, STDOUT

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
