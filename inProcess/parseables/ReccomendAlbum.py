from parseable import Parseable, RecordError
import re


class ReccomendAlbum(Parseable):
    """Reccomended Album"""
    p = re.compile(r"^\s*Album:.*")

    def __init__(self, string):
        super(ReccomendAlbum, self).__init__()
        Symbols = r"(:|~|\()"
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
        self.year =''
        for i in items:
            if i[0] == ':':
                self.title = i[1]
            elif i[0] == '~':
                self.artist = i[1]
            elif i[0] == '(':
                self.year = re.sub(r"\)", r"", i[1])

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'ReccomendAlbum.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.title, self.director, self.year, self.publisher])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)
