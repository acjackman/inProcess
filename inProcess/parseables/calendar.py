from parseable import Parseable
import re
import os


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
