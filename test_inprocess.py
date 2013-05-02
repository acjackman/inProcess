import inProcess as ip


def test_inbox_indetify():
    # Check match only one `#`
    assert ip.Inbox.identify('# Inbox')
    assert not ip.Inbox.identify('Inbox')
    assert not ip.Inbox.identify('## Inbox')

    # Check for whitespace after OK
    assert ip.Inbox.identify('# Inbox ')


def test_inbox_identify_end():
    # Either 5 `*` or 5 `-` mark the end
    assert ip.Inbox.identify_end('* * * * *')
    assert ip.Inbox.identify_end('- - - - -')

    # Can have leading or trailing whitespace
    assert ip.Inbox.identify_end(' - - - - -')   # Leading
    assert ip.Inbox.identify_end('- - - - - ')   # Trailing
    assert ip.Inbox.identify_end(' - - - - - ')  # Both


def test_inbox_multiline():
    assert ip.Inbox.multiline


def test_CMD_match():
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


def test_CMD_singleline():
    assert not ip.CMD.multiline


def test_Food_breakFline():
    # Test Divisors except units
    assert ip.Food.breakFLine('oranges') == (None, None, 'oranges', None)
    assert ip.Food.breakFLine('  oranges') == (None, None, 'oranges', None)
    assert ip.Food.breakFLine('2 oranges') == ('2', None, 'oranges', None)
    assert ip.Food.breakFLine('2 oranges') == ('2', None, 'oranges', None)
    assert ip.Food.breakFLine('*2 oranges') == ('2', None, 'oranges', None)
    assert ip.Food.breakFLine(' *2 oranges ') == ('2', None, 'oranges', None)
    assert ip.Food.breakFLine(' * 2 oranges ') == ('2', None, 'oranges', None)
    assert ip.Food.breakFLine('* 2 oranges') == ('2', None, 'oranges', None)
    assert ip.Food.breakFLine('- 2 oranges') == ('2', None, 'oranges', None)
    assert ip.Food.breakFLine('+ 2 oranges') == ('2', None, 'oranges', None)
    assert ip.Food.breakFLine('* 2 oranges --- comment') == ('2', None, 'oranges', 'comment')
    assert ip.Food.breakFLine('* 2 oranges --- comment ') == ('2', None, 'oranges', 'comment')
    assert ip.Food.breakFLine('* 2 oranges--- comment') == ('2', None, 'oranges', 'comment')
    assert ip.Food.breakFLine('* 2 oranges ---comment') == ('2', None, 'oranges', 'comment')
    assert ip.Food.breakFLine('* 2 oranges---comment') == ('2', None, 'oranges', 'comment')
    assert ip.Food.breakFLine('pizza --- comment') == (None, None, 'pizza', 'comment')
    assert ip.Food.breakFLine('2 slices pizza') == ('2', 'slices', 'pizza', None)
    assert ip.Food.breakFLine('2 slices pizza --- comment') == ('2', 'slices', 'pizza', 'comment')

    # Test all divisors
    quanties = ['oz', 'cup', 'cups', 'pack', 'packs', 'slice', 'slices',
                'piece', 'pieces', 'plate', 'plates', 'bowl', 'bowls']
    for q in quanties:
        assert ip.Food.breakFLine('2' + q + ' food') == ('2', q, 'food', None)


def test_Food_identify():
    assert ip.Food.identify('Food 2013-05-02T09:30:11')
    assert ip.Food.identify(' Food 2013-05-02T09:30:11')
    assert ip.Food.identify('Food 2013-05-02T09:30:11 ')
    assert ip.Food.identify(' Food 2013-05-02T09:30:11 ')
