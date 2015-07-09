from parseable import Parseable, RecordError
import re
import csv

class Food(Parseable):
    """Food Log parseable"""
    p = re.compile(r'\s*Food ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})')
    multiline = True

    @classmethod
    def breakFLine(cls, string):
        x = string.split('---')
        quanties = ['oz', 'cup', 'cups', 'pack', 'packs', 'slice', 'slices',
                    'piece', 'pieces', 'plate', 'plates', 'bowl', 'bowls']
        q_string = r'|'.join(quanties)
        f_mch = re.match((r"(\s*[-*]\s*)?(([\d/]+)\s*("
                          + q_string +
                          r")?\s+)?(.+)"), x[0])
        # Return tuple is ()
        # Check for comments
        if len(x) == 1:
            return (f_mch.group(3), f_mch.group(4),
                    f_mch.group(5).strip(' \t'), None)
        else:
            return (f_mch.group(3), f_mch.group(4),
                    f_mch.group(5).strip(' \t'),
                    ''.join(x[1:]).strip(' \t'))

    def __init__(self, strings):
        super(Food, self).__init__()
        strings = map(lambda s: s.strip(), strings)
        self.time = self.p.match(strings[0]).group(1)
        # Set items as strings so that you don't modify the originals, in case they need to be checked later
        self.items = strings[1:]

        # Identify and set location
        loc_idx = [i for i, s in enumerate(strings) if re.match('@.*', s)]
        if len(loc_idx) > 0:
            loc_idx = loc_idx.pop()
            self.location = re.match('@\s*(.*)', strings[loc_idx]).group(1)
            self.items.remove(strings[loc_idx])
        else:
            self.location = None

        from_idx = [i for i, s in enumerate(strings) if re.match('>.*', s)]
        if len(from_idx) > 0:
            from_idx = from_idx.pop()
            self.frm = re.match('>\s*(.*)', strings[from_idx]).group(1)
            self.items.remove(strings[from_idx])
            if self.location is None:
                self.location = self.frm
        else:
            self.frm = self.location

        self.items = map(self.breakFLine, self.items)

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'Food.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                for item in self.items:
                    spamwriter.writerow([self.time, self.location, self.frm] + list(item))
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return cls.identify_md_hr(string)