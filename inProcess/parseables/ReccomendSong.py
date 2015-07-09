from parseable import Parseable, RecordError
import re
import csv

class ReccomendSong(Parseable):
    """Reccomended Song"""
    p = re.compile(r"^\s*Song:.*")

    def __init__(self, string):
        super(ReccomendSong, self).__init__()
        Symbols = r"(:|~|a/|l/|\()"
        mstring = re.sub(Symbols, r"^^^\1", string)
        lines = mstring.split("^^^")[1:]
        keys = list()
        values = list()
        for l in lines:
            keys.append(re.sub(r"(" + Symbols + r")(.+)", r"\2", l).strip()) # Get the key
            values.append(re.sub(r"^" + Symbols, "", l).strip()) # Get the value

        items = zip(keys,values)

        self.title = ''
        self.artist = ''
        self.album = ''
        self.year = ''
        self.lyrics = ''
        for i in items:
            if i[0] == ':':
                self.title = i[1]
            elif i[0] == '~':
                self.artist = i[1]
            elif i[0] == 'a/':
                self.album = i[1]
            elif i[0] == '(':
                self.year = re.sub(r"\)", r"", i[1])
            elif i[0] == 'l/':
                self.lyrics = i[1]

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'ReccomendSong.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.title, self.artist, self.album, self.year, self.lyrics])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)
