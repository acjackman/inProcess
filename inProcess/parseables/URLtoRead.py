from parseable import Parseable, RecordError
import re
import json
import requests
from requests.auth import HTTPBasicAuth


class URLtoRead(Parseable):
    """Send URL to Instapaper"""
    p = re.compile(r"^\s*Read:\s*((https?:\/\/)?([\dA-z\.-]+)\.([A-z\.]{2,6})([0-9A-z\?=&%\./]*))\s*(.*)?")

    def __init__(self, string):
        super(URLtoRead, self).__init__()
        m_obj = self.p.match(string)
        self.URL = m_obj.group(1)
        self.comments = m_obj.group(6)

    def record(self):
        # Check for exiting credentials
        if not (('Instapaper_user' in self.settings) & ('Instapaper_password' in self.settings)):
            # If we don't have a username or password
            print "Provide Instapaper credentials in .inProcess.json. Keys: 'Instapaper_user' and 'Instapaper_password'"
            raise RecordError("Missing Instapaper username or password")

        # Try to connect & record using Instapapers Simple API
        try:
            if self.comments == '':
                payload = {'url': self.URL}
            else:
                payload = {'url': self.URL, 'selection': self.comments}

            uNp = HTTPBasicAuth(self.settings['Instapaper_user'], self.settings['Instapaper_password'])
            r = requests.get('https://www.instapaper.com/api/add', params=payload, auth=uNp)

            if r.status_code == 201:
                pass #URL added
            elif r.status_code == 400:
                raise BadRequest()
            elif r.status_code == 403:
                raise BadAuthentication()
            elif r.status_code == 403:
                raise InstaperError()

        except BadRequest as e:
            raise RecordError(e.err_msg)
        except BadAuthentication:
            raise RecordError(e.err_msg)
        except InstaperError:
            raise RecordError(e.err_msg)
        except:
            raise RecordError('Unknown error')

    class BadRequest(Exception):
        err_msg = "Bad Request: missing url? (400)"

    class BadAuthentication(Exception):
        err_msg = "Bad Authentication: Check Instapaper username/password (403)"

    class InstaperError(Exception):
        err_msg = "Instaper had a probelm \"Please try again later\" (500)"

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)
