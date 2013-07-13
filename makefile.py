all:
	make WCDB1.zip

clean:
	rm -f WCDB1.log
	rm -f WCDB1.zip
	rm -f *.pyc
	rm -rf html

turnin-list:
	turnin --list bendy cs373pj3

turnin-submit: WCDB1.zip
	turnin --submit bendy cs373pj3 WCDB1.zip

turnin-verify:
	turnin --verify bendy cs373pj3

# add other .py files

WCDB1.html: WCDB1.py
	pydoc -w WCDB1

WCDB1.log:
	git log > WCDB1.log

# add other .html and .py files

WCDB1.zip: WCDB1.html WCDB1.log WCDB1.pdf WCDB1.py WCDB1.xml WCDB1.xsd.xml TestWCDB1.py TestWCDB1.out
	zip -r WCDB1.zip  WCDB1.html WCDB1.log WCDB1.pdf WCDB1.py WCDB1.xml WCDB1.xsd.xml TestWCDB1.py TestWCDB1.out

TestWCDB1.out: TestWCDB1.py
	TestWCDB1.py > TestWCDB1.out
