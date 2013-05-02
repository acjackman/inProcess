import inProcess


def test_inbox_indetify():
    # Check match only one `#`
    assert inProcess.Inbox.identify('# Inbox')
    assert not inProcess.Inbox.identify('Inbox')
    assert not inProcess.Inbox.identify('## Inbox')

    # Check for whitespace after OK
    assert inProcess.Inbox.identify('# Inbox ')


def test_inbox_identify_end():
    # Either 5 `*` or 5 `-` mark the end
    assert inProcess.Inbox.identify_end('* * * * *')
    assert inProcess.Inbox.identify_end('- - - - -')

    # Can have leading or trailing whitespace
    assert inProcess.Inbox.identify_end(' - - - - -')   # Leading
    assert inProcess.Inbox.identify_end('- - - - - ')   # Trailing
    assert inProcess.Inbox.identify_end(' - - - - - ')  # Both


def test_inbox_multiline():
    assert inProcess.Inbox.multiline


def test_CMD_match():
    assert inProcess.CMD.identify('CMD Test')
    assert inProcess.CMD.identify('CMD  Test')    # Extra whitespace
    assert inProcess.CMD.identify(' CMD Test')    # Leading whitespace
    assert inProcess.CMD.identify('CMD Test ')    # Trailing whitespace
    assert inProcess.CMD.identify('CMD 9')        # Only numbers
    assert inProcess.CMD.identify('CMD 9Alpha9')  # letters and numbers

    # Must have a command associated
    assert not inProcess.CMD.identify('CMD')
    assert not inProcess.CMD.identify('CMD ')
    assert not inProcess.CMD.identify(' CMD')
    assert not inProcess.CMD.identify(' CMD ')


def test_CMD_singleline():
    assert not inProcess.CMD.multiline


