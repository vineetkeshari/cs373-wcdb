import re
from crises.models import WCDBElement, Crisis, Organization, Person, ListType, Text_Store, LI, R_Crisis_Person, R_Crisis_Org, R_Org_Person

def read_wcdb_model (node) :
    """
    Creates a base model with common elements
    """
    assert 'ID' in node.attrib
    assert 'Name' in node.attrib
    element_id = node.attrib['ID'].encode('ascii', 'ignore')
    element_name = node.attrib['Name'].encode('ascii', 'ignore')
    
    #assert WCDBElement.objects.get (pk=element_id) == None

    element_kind = None
    if not node.find('Kind') == None :
        element_kind = node.find('Kind').text.strip().encode('ascii', 'ignore')
    
    element_summary = None
    if not node.find('Common') == None :
        if not node.find('Common').find('Summary') == None and not node.find('Common').find('Summary').text == None:
            element_summary = node.find('Common').find('Summary').text.strip().encode('ascii', 'ignore')

    return (element_id, element_name, element_kind, element_summary)

def read_list_content (element_id, list_content_type, node, list_types, list_elements) :
    """
    Creates a ListType model along with all LI models contained in the list
    """
    assert not element_id == ''
    assert not list_content_type == ''
    list_type_id = element_id + '_' + list_content_type
    list_types.append ( ListType(ID=list_type_id, element=element_id, content_type=list_content_type, num_elements=len(node)) )
    count = 0
    for li in node :
        count = count + 1
        li_content = li_href = li_embed = li_text = None
        if not li.text == None:
            li_content = li.text.strip().encode('ascii', 'ignore')
        if 'href' in li.attrib :
            li_href = li.attrib['href']
        if 'embed' in li.attrib :
            li_embed = li.attrib['embed']
        if 'text' in li.attrib :
            li_text = li.attrib['text'].encode('ascii', 'ignore')
        list_elements.append ( LI(ID=list_type_id + '_' + str(count), ListID=list_type_id, order=count, content=li_content, href=li_href, embed=li_embed, text=li_text) )

def read_common_content (element_id, node, list_types, list_elements) :
    """
    Wrapper for reading all ListTypes under tag 'Common'
    Calls read_list_content for each list
    """
    assert not element_id == ''
    assert node.tag == 'Common'
    
    common_content_tags = ['Citations', 'ExternalLinks', 'Images', 'Videos', 'Maps', 'Feeds']
    for tag in common_content_tags :
        if not node.find(tag) == None:
            read_list_content (element_id, tag.upper(), node.find(tag), list_types, list_elements)

def get_xml_text (node, depth) :
    """
    Converts XML to indented text
    """
    my_string = ''
    attrib_print = ''
    if len(node.attrib) > 0 :
        for att in node.attrib :
            attrib_print += att + '="' + node.attrib[att] + '" '
        attrib_print = ' ' + attrib_print.strip().encode('ascii', 'ignore')
    content_print = ''
    if not node.text == None :
        content_print = node.text
    my_string += '  '*depth + '<' + node.tag + attrib_print + '>' + content_print.strip().encode('ascii', 'ignore') + '\n'
    for child in node :
        my_string += get_xml_text (child, depth+1)
    my_string += '  '*depth + '</' + node.tag + '>' + '\n'
    return my_string

def create_crisis_element (node) :
    """
    Creates a crisis model along with models for all lists contained in it
    """
    assert node.tag == 'Crisis'
    (crisis_id, crisis_name, crisis_kind, crisis_summary) = read_wcdb_model (node)

    crisis_date = None
    if not node.find('Date') == None:
        crisis_date = node.find('Date').text.strip()

    crisis_time = None
    if not node.find('Time') == None:
        crisis_time = node.find('Time').text.strip()

    new_model = Crisis (ID=crisis_id, name=crisis_name, date=crisis_date, time=crisis_time, kind=crisis_kind, summary=crisis_summary)

    list_types = []
    list_elements = []

    crisis_list_tags = ['Locations', 'HumanImpact', 'EconomicImpact', 'ResourcesNeeded', 'WaysToHelp']

    for tag in crisis_list_tags :
        if not node.find(tag) == None:
            read_list_content (crisis_id, tag.upper(), node.find(tag), list_types, list_elements)

    if not node.find('Common') == None:
        read_common_content (crisis_id, node.find('Common'), list_types, list_elements)

    xml_text = get_xml_text (node, 1)
    text_store = Text_Store (ID=crisis_id, content=xml_text)

    # Store relations
    r_co = r_cp = []
    if not node.find('Organizations') == None:
        for org in node.find('Organizations'):
            assert not org.attrib['ID'] == ''
            r_co.append(R_Crisis_Org(ID=crisis_id+'_'+org.attrib['ID'],
                        crisis=crisis_id, org=org.attrib['ID']))

    if not node.find('People') == None:
        for person in node.find('People'):
            assert not person.attrib['ID'] == ''
            r_cp.append(R_Crisis_Person(ID=crisis_id+'_'+person.attrib['ID'],
                        crisis=crisis_id, person=person.attrib['ID']))

    return (crisis_id, new_model, list_types, list_elements, r_co, r_cp, text_store)

def create_org_element (node) :
    """
    Creates an organization model along with models for all lists contained in it
    """
    assert node.tag == 'Organization'

    (org_id, org_name, org_kind, org_summary) = read_wcdb_model (node)

    org_location = None
    if not node.find('Location') == None :
        org_location = node.find('Location').text.strip().encode('ascii', 'ignore')

    new_model = Organization (ID=org_id, name=org_name, location=org_location, kind=org_kind, summary=org_summary)

    list_types = []
    list_elements = []

    if not node.find('History') == None:
        read_list_content (org_id, 'HISTORY', node.find('History'), list_types, list_elements)

    if not node.find('ContactInfo') == None:
        read_list_content (org_id, 'CONTACTINFO', node.find('ContactInfo'), list_types, list_elements)
        
    if not node.find('Common') == None:
        read_common_content (org_id, node.find('Common'), list_types, list_elements)

    xml_text = get_xml_text (node, 1)
    text_store = Text_Store (ID=org_id, content=xml_text)

    # Store relations
    r_co = r_op = []
    if not node.find('Crises') == None:
        for crisis in node.find('Crises'):
            assert not crisis.attrib['ID'] == ''
            r_co.append(R_Crisis_Org(ID=crisis.attrib['ID']+'_'+org_id,
                        crisis=crisis.attrib['ID'], org=org_id))

    if not node.find('People') == None:
        for person in node.find('People'):
            assert not person.attrib['ID'] == ''
            r_op.append(R_Org_Person(ID=org_id+'_'+person.attrib['ID'],
                        org=org_id, person=person.attrib['ID']))

    return (org_id, new_model, list_types, list_elements, r_co, r_op, text_store)

def create_person_element (node) :
    """
    Creates a person model along with models for all lists contained in it
    """
    assert node.tag == 'Person'

    (person_id, person_name, person_kind, person_summary) = read_wcdb_model (node)

    person_location = None
    if not node.find('Location') == None:
        person_location = node.find('Location').text.strip().encode('ascii', 'ignore')

    new_model = Person (ID=person_id, name=person_name, location=person_location, kind=person_kind, summary=person_summary)

    list_types = []
    list_elements = []

    if not node.find('Common') == None:
        read_common_content (person_id, node.find('Common'), list_types, list_elements)

    xml_text = get_xml_text (node, 1)
    text_store = Text_Store (ID=person_id, content=xml_text)

    # Store relations
    r_cp = r_op = []
    if not node.find('Crises') == None:
        for crisis in node.find('Crises'):
            assert not crisis.attrib['ID'] == ''
            r_cp.append(R_Crisis_Person(ID=crisis.attrib['ID']+'_'+person_id, 
                        crisis=crisis.attrib['ID'], person=person_id))

    if not node.find('Organizations') == None:
        for org in node.find('Organizations'):
            assert not org.attrib['ID'] == ''
            r_op.append(R_Org_Person(ID=org.attrib['ID']+'_'+person_id,
                        org=org.attrib['ID'], person=person_id))

    return (person_id, new_model, list_types, list_elements, r_cp, r_op, text_store)

def merge_element_content (wcdb_element) :
    list_types = []
    list_elements = []
    r_co = []
    r_cp = []
    r_op = []
    text = None
    
    return (list_types, list_elements, r_co, r_cp, r_op, text)

