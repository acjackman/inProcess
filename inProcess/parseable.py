import re

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

    def __init__(self, lines):
        super(Inbox, self).__init__()

    def record(self):
        pass

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return cls.identify_md_hr(string)

class RecordError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)