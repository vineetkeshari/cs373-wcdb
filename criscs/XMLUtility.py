from xml.etree import ElementTree as ET
from ModelFactory import create_crisis_element, create_org_element, create_person_element

def print_rec_xml (node, depth) :
    """
    For Debug: Print the read XML
    """
    attrib_print = ''
    if len(node.attrib) > 0 :
        for att in node.attrib :
            attrib_print += att + '="' + node.attrib[att] + '" '
    content_print = ''
    if not node.text == None :
        content_print = node.text
    print '  '*depth + '<' + node.tag + ' ' + attrib_print.strip() + '>' + content_print.strip()
    for child in node :
        print_rec_xml (child, depth+1)
    print '  '*depth + '</' + node.tag + '>'

def read_xml (xml_content) :
    """
    DEPRECATED: Reads xml_content from a string
    """
    xml = ET.fromstring (xml_content)
    return xml

from genxmlif import GenXmlIfError
from minixsv import pyxsval

xsd_filename = 'WCDB1.xsd.xml'

def read_and_validate_xml (filename) :
    """
    Reads and validates the XML file specified by filename

    Uses minixsv and genxmlif libraries
    Throws exceptions if the validation fails
    """
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
    """
    Initialize empty containers for all crises, orgs and people models
    """
    all_models = {}

    all_models['crises'] = {}
    all_models['people'] = {}
    all_models['orgs'] = {}

    all_models['list_types'] = []
    all_models['list_elements'] = []
    all_models['texts'] = []
    all_models['rel_crisis_org'] = []
    all_models['rel_crisis_person'] = []
    all_models['rel_org_person'] = []

    return all_models

def parse_models (root, all_models) :
    """
    Parse all models under root (<WorldCrises>) and use ModelFactory to build models
    """
    assert root.tag == 'WorldCrises'
    for child in root :
        assert child.tag in ['Crisis', 'Person', 'Organization']
        r_co = r_cp = r_op = []
        if child.tag == 'Crisis' :
            (crisis_id, new_model, list_types, list_elements, r_co, r_cp, text) = create_crisis_element (child)
            all_models['crises'][crisis_id] = new_model
        elif child.tag == 'Person' :
            (person_id, new_model, list_types, list_elements, r_cp, r_op, text) = create_person_element (child)
            all_models['people'][person_id] = new_model
        elif child.tag == 'Organization' :
            (org_id, new_model, list_types, list_elements, r_co, r_op, text) = create_org_element (child)
            all_models['orgs'][org_id] = new_model
        else :
            # should never reach here
            pass
        all_models['list_types'] += list_types
        all_models['list_elements'] += list_elements
        all_models['texts'].append(text)
        all_models['rel_crisis_org'] += r_co
        all_models['rel_crisis_person'] += r_cp
        all_models['rel_org_person'] += r_op

def parse_xml (root) :
    """
    Parses a validated XML file

    root : an Element object with 'WorldCrises' tag
    """
    assert root.tag == 'WorldCrises'
    all_models = initialize_pages ()
    parse_models (root, all_models)
    return all_models

# Call this method
def process_xml (xml_file) :
    """
    Processes an XML file by reading, validating and creating models
    """
    root = read_and_validate_xml (xml_file)
    print_rec_xml (root, 0)
    return parse_xml (root)

