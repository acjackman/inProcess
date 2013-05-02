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
