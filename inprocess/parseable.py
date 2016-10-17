import re


class Parseable(object):
    """The Parseable superclass"""
    def __init__(self):
        super(Parseable, self).__init__()
    multiline = False

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
