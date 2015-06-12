#!/usr/bin/env python
import optparse
import re
import os
from os.path import expanduser
import sys
from subprocess import Popen, PIPE, STDOUT
import csv
from datetime import datetime
import shutil
import json
import requests
from requests.auth import HTTPBasicAuth
import traceback
import sys

##############################################################################
# Parseable Class Definitions
##############################################################################


class RecordError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


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


class CMD(Parseable):
    """psudo-Parseable to match commands"""
    p = re.compile(r"\s*CMD\s+\w+")

    def __init__(self):
        super(CMD, self).__init__()

    def record(self):
        pass

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


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


class Journal(Parseable):
    """Add journal entries to Day One"""
    p = re.compile(r'\s*Journal\s+([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})')
    multiline = True

    def __init__(self, strings):
        super(Journal, self).__init__()
        strings = map(lambda s: s.strip(), strings)
        self.time = self.p.match(strings[0]).group(1)
        self.lines = strings[1:]

    def record(self):
        cmd = Popen(['dayone new'], stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=True)
        results = cmd.communicate(input='\n'.join(self.lines))
        if not results[0].startswith('New entry'):
            raise RecordError("Couldn't record journal entry")

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return cls.identify_md_hr(string)


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


class ReccomendMovie(Parseable):
    """Reccomended Movie"""
    p = re.compile(r"^\s*Movie:.*")
    
    def __init__(self, string):
        super(ReccomendMovie, self).__init__()
        Symbols = r"(:|~|w/|\(|b/)"
        mstring = re.sub(Symbols, r"^^^\1", string)
        lines = mstring.split("^^^")[1:]
        keys = list()
        values = list()
        for l in lines:
            keys.append(re.sub(r"(" + Symbols + r")(.+)", r"\2", l).strip()) # Get the key
            values.append(re.sub(r"^"+Symbols, "", l).strip()) # Get the value

        items = zip(keys,values)

        self.title = ''
        self.director = ''
        self.actors = list()
        self.year=''
        self.recBy=''
        for i in items:
            if i[0] == ':':
                self.title = i[1]
            elif i[0] == '~':
                self.director = i[1]
            elif i[0] == 'w/':
                self.actors.append(i[1])
            elif i[0] == '(':
                self.year = re.sub(r"\)", r"", i[1])
            elif i[0] == 'b/':
                self.recBy = i[1]

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'ReccomendMovie.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.title, self.director, '&'.join(self.actors), self.year, self.recBy])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

class ReccomendBook(Parseable):
    """Reccomended Book"""
    p = re.compile(r"^\s*Book:.*")
    
    def __init__(self, string):
        super(ReccomendBook, self).__init__()
        Symbols = r"(:|~|p/|\()"
        mstring = re.sub(Symbols, r"^^^\1", string)
        lines = mstring.split("^^^")[1:]
        keys = list()
        values = list()
        for l in lines:
            keys.append(re.sub(r"(" + Symbols + r")(.+)", r"\2", l).strip()) # Get the key
            values.append(re.sub(r"^" + Symbols, "", l).strip()) # Get the value

        items = zip(keys,values)

        self.title = ''
        self.author = ''
        self.publisher =''
        self.year =''
        for i in items:
            if i[0] == ':':
                self.title = i[1]
            elif i[0] == '~':
                self.author = i[1]
            elif i[0] == 'p/':
                self.publisher = i[1]
            elif i[0] == '(':
                self.year = re.sub(r"\)", r"", i[1])

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'ReccomendBook.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.title, self.author, self.year, self.publisher])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class ReccomendArtist(Parseable):
    """Reccomended Artist"""
    p = re.compile(r"^\s*Artist:.*")
    
    def __init__(self, string):
        super(ReccomendArtist, self).__init__()
        Symbols = r"(:)"
        mstring = re.sub(Symbols, r"^^^\1", string)
        lines = mstring.split("^^^")[1:]
        keys = list()
        values = list()
        for l in lines:
            keys.append(re.sub(r"(" + Symbols + r")(.+)", r"\2", l).strip()) # Get the key
            values.append(re.sub(r"^" + Symbols, "", l).strip()) # Get the value

        items = zip(keys,values)

        self.name = ''
        for i in items:
            if i[0] == ':':
                self.name = i[1]

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'ReccomendArtist.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.name])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


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


class ReccomendAuthor(Parseable):
    """Reccomended Author"""
    p = re.compile(r"^\s*Author:.*")
    
    def __init__(self, string):
        super(ReccomendAuthor, self).__init__()
        Symbols = r"(:)"
        mstring = re.sub(Symbols, r"^^^\1", string)
        lines = mstring.split("^^^")[1:]
        keys = list()
        values = list()
        for l in lines:
            keys.append(re.sub(r"(" + Symbols + r")(.+)", r"\2", l).strip()) # Get the key
            values.append(re.sub(r"^" + Symbols, "", l).strip()) # Get the value

        items = zip(keys,values)

        self.name = ''
        for i in items:
            if i[0] == ':':
                self.name = i[1]


    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'ReccomendAuthor.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.name])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


class ReccomendApp(Parseable):
    """Reccomended App"""
    p = re.compile(r"^\s*App:.*")
    
    def __init__(self, string):
        super(ReccomendApp, self).__init__()
        Symbols = r"(:|~|f/)"
        mstring = re.sub(Symbols, r"^^^\1", string)
        lines = mstring.split("^^^")[1:]
        keys = list()
        values = list()
        for l in lines:
            keys.append(re.sub(r"(" + Symbols + r")(.+)", r"\2", l).strip()) # Get the key
            values.append(re.sub(r"^" + Symbols, "", l).strip()) # Get the value

        items = zip(keys,values)

        self.name = ''
        self.developer = ''
        self.platform = ''
        for i in items:
            if i[0] == ':':
                self.name = i[1]
            elif i[0] == '~':
                self.developer = i[1]
            elif i[0] == 'f/':
                self.platform = i[1]


    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'ReccomendApp.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.name, self.developer, self.platform])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


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


class LifeTrack(Parseable):
    """Parse LifeTrack events"""
    p = re.compile((
        r"\s*Life Track:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})"
        r"\s*---\s*(?=[^\s])(.+)")
    )

    def __init__(self, string):
        super(LifeTrack, self).__init__()
        m_obj = self.p.match(string)
        self.time = m_obj.group(1)
        self.event = m_obj.group(2)

    def record(self):
        data_dir = self.settings['data_dir']
        try:
            with open(data_dir + 'LifeTrack.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.time, self.event])
        except IOError:
            raise RecordError('Problem writing to file')
        except:
            raise RecordError('Unknown error')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)


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


class Task(Parseable):
    """Add Tasks to OmniFocus"""
    p = re.compile(r'\s*!-\s*(?=[^\s])(.+)')
    multiline = True

    def __init__(self, strings):
        super(Task, self).__init__()
        self.taskstring = self.p.match(strings[0]).group(1).strip()
        if self.taskstring[-1] == '!':
            self.flagged = True
            self.taskstring = self.taskstring[:-1].strip()
        else:
            self.flagged = False
        self.notes = map(lambda s: s.strip(), strings[1:])

    def record(self):
        if self.notes == []:
            cmd_string = self.taskstring
        else:
            cmd_string = self.taskstring + " (" + '\n'.join(self.notes) + ")"
        if self.flagged:
            cmd_string = cmd_string + ' !'
        cmd = Popen(['otask', cmd_string], stdout=PIPE, stdin=PIPE,
                    stderr=STDOUT, shell=False)
        results = cmd.communicate()
        return results[0].startswith('Task added')

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

    @classmethod
    def identify_end(cls, string):
        return re.match(r"^$", string)  # Find the next empty line


class Calendar(Parseable):
    """Parse calendar events with Fantastical"""
    p = re.compile(r'\s*!@\s*(?=[^\s])(.+)')

    def __init__(self, string):
        super(Calendar, self).__init__()
        self.eventstring = self.p.match(string).group(1).strip()

    def record(self):
        os.system("osascript -e 'tell application \"Fantastical\""
                  " to parse sentence \"" + self.eventstring +
                  "\" add with immediately'")

    @classmethod
    def identify(cls, string):
        return cls.p.match(string)

##############################################################################
# Main Loop
##############################################################################


def get_now():
    return datetime.now()


def main(settings_file='~/.inprocess.json', opt_location=False):
    # Redefine Parser
    class MyParser(optparse.OptionParser):
        def format_epilog(self, formatter):
            return self.epilog

    # Parse Command Line options
    parser = MyParser(epilog=(
        '\n(c)2013 Adam Jackman (adam@acjackman.com)\n')
    )
    parser.add_option("-s", "--settings", dest="settings_file",
                      help="set settings file", metavar="FILE")
    parser.add_option('-l', '--location', action="store_true", default=False,
                      help="Print storage locations")
    options, arguments = parser.parse_args()

    # Set Variables
    if options.settings_file is not None:
        settings_file = options.settings_file
    with open(expanduser(settings_file), 'rb') as f:
        settings = json.loads(f.read())
    Parseable.settings = settings  # Pass along settings to the Parseable Class

    if options.location or opt_location:
        print('Storage Locations:\n'
              'Settings:    %s\n'
              'Inbox:       %s\n'
              'inx files:   %s\n'
              'inx storage: %s') % (settings_file, settings['inbox_file'],
                                    settings['inbox_dir'],
                                    settings['storage_dir'])
        sys.exit(0)

    # List parseable things
    parseables = Parseable.__subclasses__()  # list all direct subclasses of Parseable

    # Grab the list of inx files from the inbox directory, plus the inbox file
    files = os.listdir(settings['inbox_dir'])
    fp = re.compile(
        r"inx [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}")
    files = filter(lambda file: fp.match(file), files)
    old_files = [settings['inbox_dir'] + file for file in files]
    new_files = [settings['storage_dir'] + file for file in files]
    now = get_now()
    if os.path.exists(settings['inbox_file']):
        inbox_store = settings['storage_dir'] + "inbox " + now.strftime('%Y-%m-%dT%H-%M-%S') + ".md"
        old_files = [settings['inbox_file']] + old_files
        new_files = [inbox_store] + new_files

    # Setup output
    inbox_header = ("# Inbox\n`inbox.md` created " +
                    now.strftime('%B %d, %Y %H:%M:%S') +
                    "\n\n*" + " *"*29 + "\n\n")
    inbox_contents = ''

    # Loop through the list of files
    for f_index, file in enumerate(old_files):
        with open(file, 'rb') as f:
            line = f.readline()
            while line != '':
                for ident in parseables:
                    if ident.identify(line):
                        if ident.multiline:
                            lines = []
                            record = True
                            while ident.identify_end(line) is None:
                                lines = lines + [line]
                                line = f.readline()
                                if line == '':
                                    inbox_contents = inbox_contents + ''.join(lines) + '\n'
                                    break
                            if record:
                                try:
                                    ident(lines).record()
                                except:
                                    inbox_contents = inbox_contents + ''.join(lines) + '\n'
                        else:
                            try:
                                ident(line).record()
                            except:
                                inbox_contents = inbox_contents + line
                        break
                else:  # Runs if we don't know how to parse the current line
                    inbox_contents = inbox_contents + line
                line = f.readline()
        # After File has been processed:
        # Add blank line to remaining contents
        inbox_contents = inbox_contents + '\n\n'
        # Move the file to storage
        shutil.move(file, new_files[f_index])

    # Log inProcess run
    try:
        with open(settings['data_dir'] + 'log_inProcess.csv', 'ab') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([now])
    except IOError:
        raise RecordError('Problem writing to inProcess log')

    # Write inbox contents to file
    inbox_contents = re.sub(r'\n\s+\n', '\n\n', inbox_contents)  # Change inbox
    if re.sub('\n', '', inbox_contents) != '':
        inbox_contents = inbox_header + inbox_contents
        inbox_contents = re.sub(r"\s*\n\s*\n\s*\n+", r"\n\n", inbox_contents)
        with open(settings['inbox_file'], 'wb') as f:
            f.write(inbox_contents)

if __name__ == '__main__':
    main()
