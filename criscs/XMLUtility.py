from xml.etree import ElementTree as ET
from ModelFactory import create_crisis_element, create_org_element, create_person_element

def read_xml (filename) :
    tree = ET.parse (filename)
    return tree.getroot()

'''
from genxmlif import GenXmlIfError
from minixsv import pyxsval

xsd_filename = 'WCDB1.xsd.xml'

def read_and_validate_xml (filename) :
    try :
        elementTreeWrapper = pyxsval.parseAndValidate (filename,
                                xsdFile=xsd_filename,
                                xmlIfClass=pyxsval.XMLIF_ELEMENTTREE,
                                warningProc=pyxsval.PRINT_WARNINGS,
                                errorLimit=200, verbose=1,
                                useCaching=0, processXInclude=0 )
        elemTree = elementTreeWrapper.getTree()
        return elemTree.getroot()
    except pyxsval.XsvalError, errstr :
        print errstr
        print 'Could not validate XML files ' + xsd_filename + ' and/or ' + xsd_filename
        throw errstr
    except GenXmlIfError, errstr :
        print errstr
        print 'Could not parse XML files ' + filename + ' and/or ' + xsd_filename
        throw errstr
'''

def initialize_pages () :
    all_models = {}

    all_models['crises'] = {}
    all_models['people'] = {}
    all_models['orgs'] = {}

    all_models['list_types'] = []
    all_models['list_elements'] = []

    return all_models

def parse_models (root, all_models) :
    for child in node :
        assert child.tag in ['Crisis', 'Person', 'Organization']
        if child.tag == 'Crisis' :
            (crisis_id, new_model, list_types, list_elements) = create_crisis_element (child)
            all_models['crises'][crisis_id] = new_model
        elif child_tag == 'Person' :
            (person_id, new_model, list_types, list_elements) = create_person_element (child)
            all_models['people'][person_id] = new_model
        elif child_tag == 'Organization' :
            (org_id, new_model, list_types, list_elements) = create_org_element (child)
            all_models['orgs'][org_id] = new_model
        else :
            # should never reach here
            pass
        all_models['list_types'] += list_types
        all_models['list_elements'] += list_elements

def parse_xml (root) :
    assert root.tag == 'WorldCrises'
    all_models = initialize_pages ()
    parse_models (root, all_models)
    return all_models

# Call this method
def process_xml (filename) :
    root = read_xml (filename)
    return parse_xml (root)

