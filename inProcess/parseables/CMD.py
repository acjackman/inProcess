from parseable import Parseable, RecordError
import re


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
