from xml.etree import ElementTree as ET
from ModelFactory import create_crisis_element, create_org_element, create_person_element

def print_rec_xml (node, depth) :
    print '  '*depth + node.tag
    for child in node :
        print_rec_xml (child, depth+1)

def read_xml (xml_content) :
    xml = ET.fromstring (xml_content)
    #print_rec_xml (xml, 0)
    return xml

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
        raise Exception ('Could not validate XML files ' + xsd_filename + ' and/or ' + xsd_filename, errstr)
    except GenXmlIfError, errstr :
        raise Exception ('Could not parse XML files ' + filename + ' and/or ' + xsd_filename, errstr)

def initialize_pages () :
    all_models = {}

    all_models['crises'] = {}
    all_models['people'] = {}
    all_models['orgs'] = {}

    all_models['list_types'] = []
    all_models['list_elements'] = []

    return all_models

def parse_models (root, all_models) :
    for child in root :
        assert child.tag in ['Crisis', 'Person', 'Organization']
        if child.tag == 'Crisis' :
            (crisis_id, new_model, list_types, list_elements) = create_crisis_element (child)
            all_models['crises'][crisis_id] = new_model
        elif child.tag == 'Person' :
            (person_id, new_model, list_types, list_elements) = create_person_element (child)
            all_models['people'][person_id] = new_model
        elif child.tag == 'Organization' :
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
def process_xml (xml_file) :
    root = read_and_validate_xml (xml_file)
    return parse_xml (root)

