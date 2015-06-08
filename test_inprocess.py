import pytest
import inProcess as ip
from inProcess import RecordError
import json
from datetime import datetime  # timedelta


def general_identify_end(cls):
    # Either 5 `*` or 5 `-` mark the end
    assert cls.identify_end('* * * * *')
    assert cls.identify_end('- - - - -')

    assert cls.identify_end('*' + ' *'*29)

    # Can have leading or trailing whitespace
    assert cls.identify_end(' - - - - -')   # Leading
    assert cls.identify_end('  - - - - -')   # Leading
    assert cls.identify_end('- - - - - ')   # Trailing
    assert cls.identify_end('- - - - -  ')   # Trailing
    assert cls.identify_end(' - - - - - ')  # Both
    assert cls.identify_end('  - - - - -  ')  # Both


class TestInbox(object):
    def test_inbox_indetify(self):
        # Check match only one `#`
        assert ip.Inbox.identify('# Inbox')
        assert not ip.Inbox.identify('Inbox')
        assert not ip.Inbox.identify('## Inbox')

        # Check for whitespace after OK
        assert ip.Inbox.identify('# Inbox ')

    def test_inbox_identify_end(self):
        general_identify_end(ip.Inbox)

    def test_inbox_multiline(self):
        assert ip.Inbox.multiline


class TestCMD:
    def test_CMD_match(self):
        assert ip.CMD.identify('CMD Test')
        assert ip.CMD.identify('CMD  Test')    # Extra whitespace
        assert ip.CMD.identify(' CMD Test')    # Leading whitespace
        assert ip.CMD.identify('CMD Test ')    # Trailing whitespace
        assert ip.CMD.identify('CMD 9')        # Only numbers
        assert ip.CMD.identify('CMD 9Alpha9')  # letters and numbers

        # Must have a command associated
        assert not ip.CMD.identify('CMD')
        assert not ip.CMD.identify('CMD ')
        assert not ip.CMD.identify(' CMD')
        assert not ip.CMD.identify(' CMD ')

    def test_CMD_singleline(self):
        assert not ip.CMD.multiline


class TestFood:
    """Test the Food Parseable class"""
    def test_Food_breakFline(self):
        # Match basic name and quantity
        assert ip.Food.breakFLine('oranges') == (None, None, 'oranges', None)   # Plain item
        assert ip.Food.breakFLine('2 oranges') == ('2', None, 'oranges', None)  # Quantity
        assert ip.Food.breakFLine('Take 5') == (None, None, 'Take 5', None)     # Check number after word

        # Take care of bullets and indenting
        assert ip.Food.breakFLine('  oranges') == (None, None, 'oranges', None)      # indentation
        assert ip.Food.breakFLine('2  oranges') == ('2', None, 'oranges', None)      # Extra space between
        assert ip.Food.breakFLine('* 2 oranges') == ('2', None, 'oranges', None)     # Bullet
        assert ip.Food.breakFLine('*2 oranges') == ('2', None, 'oranges', None)      # Missing space with bullet
        assert ip.Food.breakFLine(' *2 oranges ') == ('2', None, 'oranges', None)    # indent with bullet
        assert ip.Food.breakFLine(' * 2 oranges ') == ('2', None, 'oranges', None)   # indent bullet spacing
        assert ip.Food.breakFLine(' *  2 oranges ') == ('2', None, 'oranges', None)  # indent bullet extra spacing
        assert ip.Food.breakFLine('- 2 oranges') == ('2', None, 'oranges', None)     # Other bullet characters

        # Check comments and spacing
        assert ip.Food.breakFLine('pizza --- comment') == (None, None, 'pizza', 'comment')
        assert ip.Food.breakFLine('pizza --- comment ') == (None, None, 'pizza', 'comment')
        assert ip.Food.breakFLine('pizza--- comment') == (None, None, 'pizza', 'comment')
        assert ip.Food.breakFLine('pizza ---comment') == (None, None, 'pizza', 'comment')
        assert ip.Food.breakFLine('pizza---comment') == (None, None, 'pizza', 'comment')
        assert ip.Food.breakFLine('2 slices pizza') == ('2', 'slices', 'pizza', None)
        assert ip.Food.breakFLine('2 slices pizza --- comment') == ('2', 'slices', 'pizza', 'comment')

        # Multi word comments should be allowed
        assert ip.Food.breakFLine('oranges---are really good 10/10') == (None, None, 'oranges', 'are really good 10/10')
        # Test all divisors
        quanties = ['oz', 'cup', 'cups', 'pack', 'packs', 'slice', 'slices',
                    'piece', 'pieces', 'plate', 'plates', 'bowl', 'bowls']
        for q in quanties:
            assert ip.Food.breakFLine('2' + q + ' food') == ('2', q, 'food', None)

    def test_Food_identify(self):
        assert ip.Food.identify('Food 2013-05-02T09:30:11')
        assert ip.Food.identify(' Food 2013-05-02T09:30:11')
        assert ip.Food.identify('Food 2013-05-02T09:30:11 ')
        assert ip.Food.identify(' Food 2013-05-02T09:30:11 ')

    def test_Food_identify_end(self):
        general_identify_end(ip.Food)

    def test_Journal_multline(self):
        assert ip.Food.multiline

    def test_Food_init(self):
        # Test Standard order
        fd_str = ['Food 2013-05-02T11:09:01', '1 banana', '1 bowl cereal',
                  '@ work_2', '> Home_3']
        fd_item = ip.Food(fd_str)
        assert fd_item.location == 'work_2'
        assert fd_item.frm == 'Home_3'
        assert fd_item.items == [('1', None, 'banana', None),
                                 ('1', 'bowl', 'cereal', None)]

        # Test location at the beginning
        fd_str = ['Food 2013-05-02T11:09:01', '@ work', '> Home', '1 banana']
        fd_item = ip.Food(fd_str)
        assert fd_item.location == 'work'
        assert fd_item.frm == 'Home'

        # Both Missing
        fd_str = ['Food 2013-05-02T11:09:01', '1 banana']
        fd_item = ip.Food(fd_str)
        assert fd_item.location is None
        assert fd_item.frm is None

        # Missing from or missing location should set both
        fd_str = ['Food 2013-05-02T11:09:01', '@ work', '1 banana']
        fd_item = ip.Food(fd_str)
        assert fd_item.location == 'work'
        assert fd_item.frm == 'work'
        fd_str = ['Food 2013-05-02T11:09:01', '> work',
                  'Chow Mein']
        fd_item = ip.Food(fd_str)
        assert fd_item.frm == 'work'
        assert fd_item.location == 'work'

        def check_location_and_frm(before, after, shouldbe):
            fd_str = ['Food 2013-05-02T11:09:01', before + '@' + after, 'Chow Mein']
            fd_item = ip.Food(fd_str)
            assert fd_item.location == shouldbe
            fd_str = ['Food 2013-05-02T11:09:01', before + '>' + after, 'Chow Mein']
            fd_item = ip.Food(fd_str)
            assert fd_item.frm == shouldbe

        # Multi-word from and locations should be accepted
        check_location_and_frm('', ' Panda Express', 'Panda Express')

        # Leading Space
        check_location_and_frm(' ', ' Panda', 'Panda')
        check_location_and_frm('  ', ' Panda', 'Panda')

        # Trailing Space
        check_location_and_frm('', ' Panda ', 'Panda')
        check_location_and_frm('', ' Panda  ', 'Panda')

        # Space between delimiter
        check_location_and_frm('', 'Panda ', 'Panda')  # Missing
        check_location_and_frm('', '  Panda ', 'Panda')  # Extra


class TestJournal:
    def test_Journal_identify(self):
        assert ip.Journal.identify('Journal 2013-05-02T13:17:46')
        assert ip.Journal.identify('Journal  2013-05-02T13:17:46')
        assert ip.Journal.identify('Journal 2013-05-02T13:17:46 ')
        assert ip.Journal.identify(' Journal 2013-05-02T13:17:46')
        assert ip.Journal.identify(' Journal 2013-05-02T13:17:46 ')
        assert not ip.Journal.identify('Jornal 2013-05-02T13:17:46')

    def test_Journal_identify_end(self):
        general_identify_end(ip.Journal)

    def test_Journal_multline(self):
        assert ip.Journal.multiline

    def test_Journal_initialize(self):
        lines = ['P1 About four years. I got tired of hearing how young I looked.'
                 '',
                 'P2 About four years. I got tired of hearing how young I looked.']
        jrnl = ip.Journal(['Journal 2013-05-02T13:33:04'] + lines)
        assert jrnl.time == '2013-05-02T13:33:04'
        assert jrnl.lines == lines


class TestStatistic:
    def test_Statistic_identify(self):
        assert ip.Statistic.identify('Statistic. 2013-05-02T14:18:26')
        assert ip.Statistic.identify('Statistic. 2013-05-02T14:18:26. Test')
        assert ip.Statistic.identify('Statistic. 2013-05-02T14:18:26. Test. Test_2')
        assert not ip.Statistic.identify('Statistic: 2013-05-02T14:18:26')
        assert not ip.Statistic.identify('Statistic.2013-05-02T14:18:26')

    def test_Statistic_initialize(self):
        def s_check(string, name, time, extras=[]):
            st = ip.Statistic(string)
            print st
            assert st.StatName == name
            assert st.time == time
            assert st.extras == extras

        s_check('Test. 2013-05-02T19:30:47', 'Test', '2013-05-02T19:30:47')
        s_check('Test. 2013-05-02T19:30:47. ', 'Test', '2013-05-02T19:30:47')
        s_check('Evening Prayer. 2013-05-02T19:34:51', 'Evening Prayer',
                '2013-05-02T19:34:51')
        s_check('Sleep. 2013-05-02T19:35:06. 2013-05-02T19:43:43', 'Sleep',
                '2013-05-02T19:35:06', extras=['2013-05-02T19:43:43'])
        s_check('Book. 2013-05-02T19:51:41. Author. Title. 230', 'Book',
                '2013-05-02T19:51:41', extras=['Author', 'Title', '230'])


class TestRecommendMovie:
    def test_RecommendMovie_identify(self):
        assert ip.ReccomendMovie.identify('Movie: Age of Ultron')
        assert ip.ReccomendMovie.identify(' Movie: Age of Ultron')
        assert ip.ReccomendMovie.identify(' Movie: Age of Ultron w/ Captain America')
        assert ip.ReccomendMovie.identify(' Movie: Age of Ultron w/ Captain America (2015)    ')
        assert not ip.ReccomendMovie.identify('Movie. 2013-05-02T14:18:26')

    def test_ReccomendMovie_initialize(self):
        def s_check(string, title='', director='', actors=[], year='', recBy=''):
            rm = ip.ReccomendMovie(string)
            print rm
            assert rm.title == title
            assert rm.director == director
            assert rm.actors == actors
            assert rm.year == year
            assert rm.year == year
            assert rm.recBy == recBy

        s_check('Movie: Age of Ultron', 'Age of Ultron')
        s_check('Movie: ~ Joss Weadon', director='Joss Weadon')
        s_check('Movie: (1234)', year='1234')
        s_check('Movie: w/ Captain America', actors=['Captain America'])
        s_check('Movie: w/Captain America', actors=['Captain America'])
        s_check('Movie: w/Captain America ', actors=['Captain America'])
        s_check('Movie: w/ Captain America w/ Thor', actors=['Captain America', 'Thor'])
        s_check('Movie: b/ Everyone and their Brother', recBy='Everyone and their Brother')
        s_check('Movie: Age of Ultron ~ Joss Weadon (1234) w/ Captain America w/ Thor b/ Everyone and their Brother', 
            title='Age of Ultron',
            director='Joss Weadon',
            actors=['Captain America', 'Thor'],
            year='1234',
            recBy='Everyone and their Brother')

class TestRecommendBook:
    def test_RecommendBook_identify(self):
        assert ip.ReccomendBook.identify('Book: Age of Ultron')
        assert ip.ReccomendBook.identify(' Book: Age of Ultron')
        assert ip.ReccomendBook.identify(' Book: Age of Ultron w/ Captain America')
        assert ip.ReccomendBook.identify(' Book: Age of Ultron w/ Captain America (2015)    ')
        assert not ip.ReccomendBook.identify('Book. 2013-05-02T14:18:26')

    def test_ReccomendBook_initialize(self):
        def s_check(string, title='', author='', publisher='', year=''):
            rm = ip.ReccomendBook(string)
            assert rm.title == title
            assert rm.author == author
            assert rm.publisher == publisher
            assert rm.year == year

        s_check('Book: Book 1', title='Book 1')
        s_check('Book: Book 1 p/ Random Place', title='Book 1', publisher='Random Place')
    
        s_check('Book: Book 1 ~ Moroni (1234) p/ Random Place', 
            title='Book 1',
            author='Moroni',
            year='1234',
            publisher='Random Place')



class TestLifeTrack:
    def test_LifeTrack_identify(self):
        assert ip.LifeTrack.identify('Life Track: 2013-05-02T19:59:26 --- Event')
        assert ip.LifeTrack.identify(' Life Track: 2013-05-02T19:59:26 --- Event')
        assert ip.LifeTrack.identify('  Life Track: 2013-05-02T19:59:26 --- Event')
        assert ip.LifeTrack.identify('Life Track:2013-05-02T19:59:26 --- Event')
        assert ip.LifeTrack.identify('Life Track:  2013-05-02T19:59:26 --- Event')
        assert ip.LifeTrack.identify('Life Track: 2013-05-02T19:59:26 --- Event with words')
        assert ip.LifeTrack.identify('Life Track: 2013-05-02T19:59:26 ---  Event')
        assert ip.LifeTrack.identify('Life Track: 2013-05-02T19:59:26 ---Event')
        assert ip.LifeTrack.identify('Life Track: 2013-05-02T19:59:26--- Event')
        assert not ip.LifeTrack.identify('Life Track: 2013-05-02T19:59:26--- ')
        assert not ip.LifeTrack.identify('Life Track: 2013-05-02T19:59:26---  ')

    def test_LifeTrack_initialize(self):
        lt = ip.LifeTrack('Life Track: 2013-05-02T20:18:14 --- Event that has description')
        assert lt.time == '2013-05-02T20:18:14'
        assert lt.event == 'Event that has description'


class TestHealthTrack:
    def test_HealthTrack_identify(self):
        assert ip.HealthTrack.identify('Health Track: 2013-05-02T19:59:26 --- Event')
        assert ip.HealthTrack.identify(' Health Track: 2013-05-02T19:59:26 --- Event')
        assert ip.HealthTrack.identify('  Health Track: 2013-05-02T19:59:26 --- Event')
        assert ip.HealthTrack.identify('Health Track:2013-05-02T19:59:26 --- Event')
        assert ip.HealthTrack.identify('Health Track:  2013-05-02T19:59:26 --- Event')
        assert ip.HealthTrack.identify('Health Track: 2013-05-02T19:59:26 --- Event with words')
        assert ip.HealthTrack.identify('Health Track: 2013-05-02T19:59:26 ---  Event')
        assert ip.HealthTrack.identify('Health Track: 2013-05-02T19:59:26 ---Event')
        assert ip.HealthTrack.identify('Health Track: 2013-05-02T19:59:26--- Event')
        assert not ip.HealthTrack.identify('Health Track: 2013-05-02T19:59:26--- ')
        assert not ip.HealthTrack.identify('Health Track: 2013-05-02T19:59:26---  ')

    def test_HealthTrack_initialize(self):
        lt = ip.HealthTrack('Health Track: 2013-05-02T20:18:14 --- Event that has description')
        assert lt.time == '2013-05-02T20:18:14'
        assert lt.event == 'Event that has description'


class TestTask:
    def test_Task_identify(self):
        assert ip.Task.identify('!- Task')
        assert ip.Task.identify('!-Task')
        assert ip.Task.identify('!- Test Task')
        assert ip.Task.identify('!- Test Task ')
        assert ip.Task.identify('!-  Test Task  ')
        assert ip.Task.identify('!-  Test Task !')
        assert ip.Task.identify('!-  Test Task!')
        assert ip.Task.identify('!-  Test Task ! ')
        assert not ip.Task.identify('- Test Task')
        assert not ip.Task.identify('! Test Task')
        assert not ip.Task.identify('Test Task')
        assert not ip.Calendar.identify('!-')
        assert not ip.Calendar.identify('!- ')
        assert not ip.Calendar.identify('!-  ')

    def test_task_multiline(self):
        assert ip.Task.multiline

    def test_task_initialize(self):
        def t_check(strings, task, notes=[], f=False):
            t = ip.Task(strings)
            assert t.taskstring == task
            assert t.notes == notes
            assert t.flagged == f

        # Check Basic Tag creation
        t_check(['!- Task'], 'Task')
        t_check([' !- Task'], 'Task')
        t_check(['!- Task '], 'Task')
        t_check(['!-  Task '], 'Task')
        t_check(['!-Task'], 'Task')
        t_check(['!- Task String that is long'], 'Task String that is long', f=False)

        # Check Flag
        t_check(['!- Task String that is long !'], 'Task String that is long', f=True)
        t_check(['!- Task !'], 'Task', f=True)
        t_check(['!- Task!'], 'Task', f=True)
        t_check(['!- Task !'], 'Task', f=True)
        t_check(['!- DoSomething! !'], 'DoSomething!', f=True)
        t_check(['!- DoSomething!!'], 'DoSomething!', f=True)
        t_check(['!- DoSomething!'], 'DoSomething', f=True)
        t_check(['!- DoSomething!else'], 'DoSomething!else', f=False)


class TestCalendar:
    def test_Calendar_identify(self):
        assert ip.Calendar.identify('!@ Event')
        assert ip.Calendar.identify('!@  Event')
        assert ip.Calendar.identify(' !@ Event')
        assert ip.Calendar.identify('!@Event')
        assert not ip.Calendar.identify('!- Event')
        assert not ip.Calendar.identify('@ Event')
        assert not ip.Calendar.identify('!@')
        assert not ip.Calendar.identify('!@ ')
        assert not ip.Calendar.identify('!@  ')

    def test_Calendar_initialize(self):
        def c_check(string, event):
            c = ip.Calendar(string)
            assert c.eventstring == event

        c_check('!@ Event', 'Event')
        c_check('!@  Event', 'Event')
        c_check('!@ Event ', 'Event')
        c_check('!@ Event at 4pm /w ', 'Event at 4pm /w')


class FunctionalBase:
    def create_env(self, tdir):
        self.set_file = tdir.join("settings.json")
        self.inbox_dir = tdir.mkdir("Inbox")
        self.inbox_file = tdir.join("inbox.md")
        self.data_dir = tdir.mkdir("Data")
        self.storage_dir = tdir.mkdir("LogStorage")
        tmp_settings = {
            "inbox_dir": str(self.inbox_dir.realpath()) + '/',
            "inbox_file": str(self.inbox_file.realpath()),
            "data_dir": str(self.data_dir.realpath()) + '/',
            "storage_dir": str(self.storage_dir.realpath()) + '/'
        }
        self.set_file.write(json.dumps(tmp_settings))

    def create_inbox_file(self, contents, created=datetime(2013, 5, 1, 8, 0, 0)):
        contents = ("# Inbox\n`inbox.md` created " +
                    created.strftime('%B %d, %Y %H:%M:%S') +
                    "\n\n\n*" + " *"*5 + "\n" + contents)
        self.inbox_file.write(contents)

    def create_inxfile(self, date, contents, ext='md'):
        inx = self.inbox_dir.join("inx " + date.strftime('%Y-%m-%dT%H-%M-%S') + '.' + ext)
        inx.write(contents)

    def run_inProcess(self):
        ip.main(settings_file=str(self.set_file.realpath()))

    def inbox_exits(self, true=True):
        if true:
            assert self.inbox_file.check()
        else:
            assert not self.inbox_file.check()

    def num_files_inbox(self, num):
        assert len(self.inbox_dir.listdir()) == num

    def num_files_storage(self, num):
        assert len(self.storage_dir.listdir()) == num

    def check_inbox_contents(self, values):
        lines = self.inbox_file.read().splitlines()
        for line_num, line in values.iteritems():
            assert lines[line_num] == line

    def check_inbox_length(self, num_lines):
        lines = self.inbox_file.read().splitlines()
        assert len(lines) == num_lines


class TestBasicFunctional(FunctionalBase):
    def test_create_inbox(self, tmpdir, monkeypatch):
        self.create_env(tmpdir)
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), 'test')

        def mock_now():
            return datetime(2013, 5, 1, 12, 30, 0, 0)
        monkeypatch.setattr(ip, 'get_now', mock_now)

        self.run_inProcess()

        self.num_files_inbox(0)
        self.num_files_storage(1)
        self.inbox_exits()
        # Check inbox contents
        self.check_inbox_contents(
            {0: '# Inbox',
             1: '`inbox.md` created May 01, 2013 12:30:00',
             2: '',
             3: '*' + ' *'*29,
             4: '',
             5: 'test',
             6: ''})
        self.check_inbox_length(7)

    def test_read_inbox(self, tmpdir):
        self.create_env(tmpdir)
        # Check inbox remains the same
        self.create_inbox_file('Test')
        self.run_inProcess()
        self.check_inbox_contents({5: 'Test'})

        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 34), 'Test_2')
        self.run_inProcess()
        self.check_inbox_contents({5: 'Test', 7: 'Test_2'})

    def test_multiple_files(self, tmpdir):
        self.create_env(tmpdir)
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), 'Test')
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 34), 'Test_2')
        self.run_inProcess()
        self.check_inbox_contents({5: 'Test', 7: 'Test_2'})

    def test_HealthTrack_record_basic(self, tmpdir):
        self.create_env(tmpdir)
        # Check that HealthTrack records properly, with no inbox
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), 'Health Track: 2013-05-03T20:24:20 --- Test')
        self.run_inProcess()
        self.inbox_exits(False)
        assert self.data_dir.join('HealthTrack.csv').check()

    def test_HealthTrack_record_Exception(self, tmpdir, monkeypatch):
        self.create_env(tmpdir)

        def mock_record(self):
            raise RecordError('Unknown error')
        monkeypatch.setattr(ip.HealthTrack, 'record', mock_record)
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), 'Health Track: 2013-05-03T20:24:20 --- Test')
        self.run_inProcess()
        self.inbox_exits(True)
        monkeypatch.undo()

    @pytest.mark.skipif("True")
    def test_HealthTrack_record_missing_data_dir(self, tmpdir):
        self.create_env(tmpdir)
        # With Missing Data Dir
        self.data_dir.remove()
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), 'Health Track: 2013-05-03T21:05:47 --- Test')
        self.run_inProcess()
        assert not self.data_dir.check()
        self.inbox_exits()

    def test_no_empty_inbox(self, tmpdir):
        self.create_env(tmpdir)
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), '')
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), ' ')
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), '\n\n\n')
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), '\n  \n \n')
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), '\n\t \t \n \n')
        self.run_inProcess()
        self.inbox_exits(true=False)

    def test_remove_whitespace_on_blanklines(self, tmpdir):
        cnts = ('the next line should not have whitespace:\n'
                '  \n'
                'also the next line\n'
                '\t\n'
                'but there should be three distinct paragraphs\n')
        self.create_env(tmpdir)
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33), cnts)
        self.run_inProcess()
        self.check_inbox_contents({6: '', 8: ''})

    def test_incomplete_multiline(self, tmpdir):
        self.create_env(tmpdir)
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 33),
                            'Journal 2013-05-04T20:49:02')
        self.create_inxfile(datetime(2013, 5, 3, 16, 21, 34),
                            'Test. 2013-05-04T21:03:25')
        self.run_inProcess()
        self.check_inbox_contents({5: 'Journal 2013-05-04T20:49:02'})
        assert self.data_dir.join('Test.csv').check()

    def test_inProcess_log(self, tmpdir):
        self.create_env(tmpdir)
        self.run_inProcess()
        assert self.data_dir.join('log_inProcess.csv').check()
