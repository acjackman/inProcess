from parseable import Parseable, RecordError
import re
from subprocess import Popen, PIPE, STDOUT


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
