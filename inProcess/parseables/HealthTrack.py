from parseable import Parseable, RecordError
import re
import csv


class HealthTrack(Parseable):
    """Parse HealthTrack events"""
    p = re.compile((
        r"\s*Health Track:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})"
        r"\s*---\s*(?=[^\s])(.+)")
    )

    def __init__(self, string):
        super(HealthTrack, self).__init__()
        m_obj = self.p.match(string)
        self.time = m_obj.group(1)
        self.event = m_obj.group(2)

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'HealthTrack.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.time, self.event])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)
