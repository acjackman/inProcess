import inProcess as ip
import os
import json
from datetime import datetime, timedelta


def general_identify_end(cls):
    # Either 5 `*` or 5 `-` mark the end
    assert cls.identify_end('* * * * *')
    assert cls.identify_end('- - - - -')

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

        # Multi word comments should be alowed
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
        tmp_settings = {
            "inbox_dir": str(self.inbox_dir.realpath()) + '/',
            "inbox_file": str(self.inbox_file.realpath()),
            "data_dir": str(self.data_dir.realpath()) + '/',
            "storage_dir": str(tdir.mkdir("LogStorage").realpath()) + '/'
        }
        self.set_file.write(json.dumps(tmp_settings))

    def create_inxfile(self, date, contents, ext='md'):
        inx = self.inbox_dir.join("inx " + date + '.' + ext)
        inx.write(contents)

    def run_inProcess(self):
        ip.main(settings_file=str(self.set_file.realpath()))


class TestBasicFunctional(FunctionalBase):
    def test_create_inbox(self, tmpdir):
        self.create_env(tmpdir)
        self.create_inxfile('2013-05-03T16-21-33', 'test')
        self.run_inProcess()
        assert len(self.inbox_dir.listdir()) == 0
        assert self.inbox_file.check()
