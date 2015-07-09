from parseable import Parseable, RecordError
import re
import csv

class Statistic(Parseable):
    """Tack statistics that are not otherwise matched"""
    p = re.compile((
        r"\s*([A-z 0-9]+)\. "
        r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})"
        r"(.*)")
    )

    def __init__(self, string):
        super(Statistic, self).__init__()
        m_obj = self.p.match(string)
        self.StatName = m_obj.group(1)
        self.time = m_obj.group(2)
        self.extras = filter(None, m_obj.group(3).split('. '))

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + self.StatName.replace(' ', '')+'.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.time] + self.extras)
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)