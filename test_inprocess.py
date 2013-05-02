import inProcess as ip


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
