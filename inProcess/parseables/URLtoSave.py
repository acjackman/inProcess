from parseable import Parseable, RecordError
import re
import json
import requests
from requests.auth import HTTPBasicAuth


class URLtoSave(Parseable):
    """Save URL to Pinboard"""
    p = re.compile(r"^\s*Save:\s*((https?:\/\/)?([\dA-z\.-]+)\.([A-z\.]{2,6})([-0-9A-z\?=&%\./]*))\s*---\s*(.+)")
    multiline = True

    def __init__(self, strings):
        super(URLtoSave, self).__init__()
        m_obj = self.p.match(strings[0])
        self.payload = {'url': m_obj.group(1)}
        if len(strings) > 1:
            self.payload['extended'] = ''.join(strings[1:]) # Extended notes
        self.payload['shared'] = 'yes' # public='yes', private='no'
        self.payload['toread'] = 'no'
        self.payload['replace'] = 'no'

        # Break up part
        p_data_string = m_obj.group(6)
        p_shared = re.compile(r'(.*) p/(.*)')
        if re.match(p_shared, p_data_string):
            self.payload['shared'] = 'no'
            p_data_string = re.sub(p_shared, r'\1 \2', p_data_string)

        p_readlater = re.compile(r'(.*) r/(.*)')
        if re.match(p_readlater, p_data_string):
            self.payload['toread'] = 'yes'
            p_data_string = re.sub(p_readlater, r'\1 \2', p_data_string)

        self.tags = ['.AddinProcess']
        p_tag = re.compile(r'(.*)#([\.\w]+)(\s+.*|$)')
        m = p_tag.match(p_data_string)
        while m:
            self.tags.append(m.group(2))
            p_data_string = (m.group(1)+" "+m.group(3)).strip()
            m = p_tag.match(p_data_string)

        self.payload['description'] = p_data_string.strip() # One line title/description

    def record(self):
        try:
            self.payload['auth_token']= self.settings['pinboard_api_token']
            self.payload['tags']= ' '.join(self.tags)
            r = requests.get('https://api.pinboard.in/v1/posts/add', params=self.payload)

            if r.status_code == 200:
                result_code = re.search(r'<result code="(.*)" />', r.text).group(1)
                if result_code == 'done':
                    pass # URL added
                elif result_code == 'item already exists':
                    print "Pinboard item already exits for url: " + self.payload['url']

                elif result_code == 'missing url':

                    raise RecordError ("Don't know how you managed to not have a URL, but there's not one that I can see")
            elif r.status_code == 429:
                print "Submitting to many requests, slow down"
                raise ToManyPinboardRequests()

        except:
            raise RecordError('Unknown error')

    class ToManyPinboardRequests(Exception):
        err_msg = "You have submitted too many requests to the Pinboard API, give it a rest and try again later (429)"

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return re.match(r"^$", string)  # Find the next empty line