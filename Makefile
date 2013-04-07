default:
	echo 'No Default'

deploy:
	cp inProcess.py ~/Dropbox/Library/bin/inProcess

TestData:
	@mkdir -p Test/Data
	@mkdir -p Test/Inbox
	@mkdir -p Test/LogStorage
	@touch Test/LogStorage/f
	@rm Test/LogStorage/*
	@touch Test/inbox/inxf
	@rm Test/inbox/inx*
	@touch Test/Data/f
	@rm Test/Data/*
	@echo 'Test. 2013-04-06T14:37:18' > 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo 'Sleep. 2013-04-06T14:37:18. 2013-04-06T14:37:18' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo 'Food 2013-04-07T04:21:44' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '2 oranges' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '@ home' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '* * * * * *' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo 'Journal 2013-04-07T04:21:44' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium.' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim.' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '@ home' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '* * * * * *' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '!- Test Single line' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '!- Test Multiple Lines' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '* Note 1' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '* Note 2' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '* Note 3' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo '' >> 'Test/Inbox/inx 2013-04-06T14-37-18.md'
	@echo 'Test. 2013-04-06T22:19:30' > 'Test/Inbox/inx 2013-04-08T00-00-00.md'
	@echo '' >> 'Test/Inbox/inx 2013-04-08T00-00-00.md'
	@echo 'Sleep. 2013-04-06T22:16:58. 2013-04-07T22:16:58' >> 'Test/Inbox/inx 2013-04-08T00-00-00.md'
	@echo '' >> 'Test/Inbox/inx 2013-04-08T00-00-00.md'
	@echo 'Newline. 2013-04-06T14:37:18. 2013-04-06T14:37:18' >> 'Test/Inbox/inx 2013-04-08T00-00-00.md'
	@echo '# Inbox' > 'Test/inbox.md'
	@echo '`inbox.md` created April 06, 2013 20:36' >> 'Test/inbox.md'
	@echo '' >> 'Test/inbox.md'
	@echo '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * *' >> 'Test/inbox.md'
	@echo '' >> 'Test/inbox.md'
	@echo '{"inbox_dir": "/Users/Adam/Dropbox/Active/inProcess/Test/Inbox/","inbox_file": "/Users/Adam/Dropbox/Active/inProcess/Test/inbox.md","data_dir": "/Users/Adam/Dropbox/Active/inProcess/Test/Data/","storage_dir": "/Users/Adam/Dropbox/Active/inProcess/Test/LogStorage/"}'> 'Test/.inprocess.json'
