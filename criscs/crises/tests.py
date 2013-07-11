"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import unittest
import xml.etree.ElementTree as ET
from ModelFactory import create_crisis_element, create_org_element, create_person_element, read_wcdb_model, read_list_content
from XMLUtility import print_rec_xml, initialize_pages, parse_models, parse_xml, process_xml, read_and_validate_xml
from crises.models import WCDBElement, Crisis, Organization, Person, ListType, LI, R_Crisis_Person, R_Crisis_Org, R_Org_Person
from genxmlif import GenXmlIfError
from minixsv import pyxsval
from django.test.simple import DjangoTestSuiteRunner

class NoTestDbDatabaseTestRunner(DjangoTestSuiteRunner):
    #Override setup and teardown of databases to force test runner to work.
    def setup_databases(self, **kwargs):
        pass
    def teardown_databases(self, old_config, **kwargs):
        pass

####
####Begin tests
####

class TestXMLUtility (unittest.TestCase) :
	def test_process_xml_1(self) :
		testXMLFile = "crises/test_data/WorldCrises_good.xml"
		model = process_xml(testXMLFile)
		assert(len(model) == 5)
		assert(len(model["crises"])==1)
		assert(type(model["crises"]["CRI_NRINFL"]) is Crisis)
		assert(len(model["people"])==1)
		assert(type(model["people"]["PER_MNSNGH"]) is Person)
		assert(len(model["orgs"])==1)
		assert(type(model["orgs"]["ORG_PMRLFD"]) is Organization)

	def test_process_xml_2(self) :
		try :
			testXMLFile = "crises/test_data/WorldCrises_bad_root.xml"
			model = process_xml(testXMLFile)	
			assert(False)
		except :
			assert(True)

	def test_process_xml_3(self) :
		try :
			testXMLFile = ""
			model = process_xml(testXMLFile)	
			assert(False)
		except :
			assert(True)

	def test_initialize_pages_1(self) :
		all_models = initialize_pages()
		assert(len(all_models) == 5)
		assert("crises" in all_models)
		assert("list_types" in all_models)
		assert("orgs" in all_models)
		assert("list_types" in all_models)
		assert("list_elements" in all_models)

	def test_read_and_validate_xml_1(self) :
		testXMLFile = "crises/test_data/WorldCrises_good.xml"
		model = read_and_validate_xml(testXMLFile)
		assert (model is not None)

	def test_read_and_validate_xml_2(self) :
		testXMLFile = "crises/test_data/WorldCrises_bad_root.xml"
		try :
			model = read_and_validate_xml(testXMLFile)
			assert(False)
		except :
			assert(True)

	def test_read_and_validate_xml_3(self) :
		testXMLFile = "crises/test_data/WorldCrises_bad_id.xml"
		try :
			model = read_and_validate_xml(testXMLFile)
			assert(False)
		except :
			assert(True)	

	def test_parse_xml_1(self) :
		testXMLFile = "crises/test_data/WorldCrises_good.xml"
		xml = read_and_validate_xml(testXMLFile)
		model = parse_xml (xml)
		assert(len(model) == 5)
		assert(len(model["crises"])==1)
		assert(type(model["crises"]["CRI_NRINFL"]) is Crisis)
		assert(len(model["people"])==1)
		assert(type(model["people"]["PER_MNSNGH"]) is Person)
		assert(len(model["orgs"])==1)
		assert(type(model["orgs"]["ORG_PMRLFD"]) is Organization)

	def test_parse_xml_2(self) :
		try :
			testXMLFile = "crises/test_data/WorldCrises_bad_root.xml"
			xml = read_and_validate_xml(testXMLFile)
			model = parse_xml (xml)	
			assert(False)
		except :
			assert(True)

	def test_parse_xml_3(self) :
		try :
			testXMLFile = ""
			xml = read_and_validate_xml(testXMLFile)
			model = parse_xml (xml)		
			assert(False)
		except :
			assert(True)

	def test_print_rec_xml_1(self) :
		try :
			testXMLFile = "crises/test_data/WorldCrises_good.xml"
			xml = read_and_validate_xml(testXMLFile)
			print_rec_xml(xml, 0)
			assert(True)
		except :
			assert(False)

	def test_parse_models_1(self) :
		testXMLFile = "crises/test_data/WorldCrises_good.xml"
		root = read_and_validate_xml (testXMLFile)
		model = initialize_pages ()
		parse_models (root, model)
		assert(len(model) == 5)
		assert(len(model["crises"])==1)
		assert(type(model["crises"]["CRI_NRINFL"]) is Crisis)
		assert(len(model["people"])==1)
		assert(type(model["people"]["PER_MNSNGH"]) is Person)
		assert(len(model["orgs"])==1)
		assert(type(model["orgs"]["ORG_PMRLFD"]) is Organization)

	def test_parse_models_2(self) :
		try :
			testXMLFile = "crises/test_data/WorldCrises_good.xml"
			root = read_and_validate_xml (testXMLFile)
			model = initialize_pages ()
			parse_models (root, model)
			assert(False)
		except :
			assert(True)

	def test_parse_models_3(self) :
		try :
			testXMLFile = "crises/test_data/WorldCrises_good.xml"
			root = read_and_validate_xml (testXMLFile)
			model = initialize_pages ()
			parse_models (root, model)	
			assert(False)
		except :
			assert(True)

		

#class TestModelFactory (unittest.TestCase) :
#	def test_create_crisis_element_1(self) :
#		testXMLFile = "crises/WorldCrises.example.xml"
#		testXML = open(testXMLFile, 'r').read()



		
