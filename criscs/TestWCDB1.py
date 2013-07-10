"""
To test the program:
    % python TestWCDB1.py >& TestWCDB1.py.out
    % chmod ugo+x TestXML.py
    % TestWCDB1.py >& TestWCDB1.py.out
"""

# -------
# imports
# -------

import StringIO
import unittest
import xml.etree.ElementTree as ET

from XMLUtility import print_rec_xml, read_xml, initialize_pages, parse_models, parse_xml, process_xml

# -----------
# TestXMLUtility
# -----------

class TestXMLUtility (unittest.TestCase) :

	def test_print_rec_xml_1 (self) :
	  	print '  '*depth + node.tag
	   	self.assert_(true)


print "TestWCDB1.py"
unittest.main()
print "Done."