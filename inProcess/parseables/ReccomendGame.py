from parseable import Parseable, RecordError
import re
import csv


class ReccomendGame(Parseable):
    """Reccomended Game"""
    p = re.compile(r"^\s*Game:.*")

    def __init__(self, string):
        super(ReccomendGame, self).__init__()
        Symbols = r"(:|~|g/)"
        mstring = re.sub(Symbols, r"^^^\1", string)
        lines = mstring.split("^^^")[1:]
        keys = list()
        values = list()
        for l in lines:
            keys.append(re.sub(r"(" + Symbols + r")(.+)", r"\2", l).strip()) # Get the key
            values.append(re.sub(r"^" + Symbols, "", l).strip()) # Get the value

        items = zip(keys,values)

        self.name = ''
        self.publisher = ''
        self.genre = ''
        for i in items:
            if i[0] == ':':
                self.name = i[1]
            elif i[0] == '~':
                self.publisher = i[1]
            elif i[0] == 'g/':
                self.genre = i[1]

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'ReccomendGame.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.name, self.publisher, self.genre])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)
