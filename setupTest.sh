rm Test/Data/*
rm Test/Inbox/inx*
rm Test/LogStorage/*
rm 'Test/inbox.md'

echo 'Test. 2013-04-06T14:37:18' > 'Test/Inbox/inx 2013-04-06T14-37-18.md'
echo '' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
echo 'Sleep. 2013-04-06T14:37:18. 2013-04-06T14:37:18' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
echo '' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
echo 'Regular Text' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
echo '' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
echo -n 'No Newline. 2013-04-06T14:37:18. 2013-04-06T14:37:18' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'

echo 'Test. 2013-04-06T22:19:30' > 'Test/Inbox/inx 2013-04-08T00-00-00.md'
echo '' >> 'Test/Inbox/inx 2013-04-08T00-00-00.md'
echo 'Sleep. 2013-04-06T22:16:58. 2013-04-07T22:16:58' >> 'Test/Inbox/inx 2013-04-08T00-00-00.md'
echo '' >> 'Test/Inbox/inx 2013-04-08T00-00-00.md'
echo '!- Test Task' >> 'Test/Inbox/inx 2013-04-08T00-00-00.md'
echo '' >> 'Test/Inbox/inx 2013-04-08T00-00-00.md'
echo 'Newline. 2013-04-06T14:37:18. 2013-04-06T14:37:18' >> 'Test/Inbox/inx 2013-04-08T00-00-00.md'

echo '# Inbox' > 'Test/inbox.md'
echo '`inbox.md` created April 06, 2013 20:36' >> 'Test/inbox.md'
echo '' >> 'Test/inbox.md'
echo '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * *' >> 'Test/inbox.md'
echo '' >> 'Test/inbox.md'
