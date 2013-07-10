from crises.models import WCDBElement, Crisis, Organization, Person, ListType, LI, R_Crisis_Person, R_Crisis_Org, R_Org_Person

def read_wcdb_model (node) :
    for i in node:
        print i
    assert 'ID' in node.attrib
    assert 'Name' in node.attrib
    element_id = node.attrib['ID']
    element_name = node.attrib['Name']
    
    #assert WCDBElement.objects.get (pk=element_id) == None

    element_kind = None
    if not node.find('Kind') == None :
        element_kind = node.find('Kind').text.strip()
    
    element_summary = None
    if not node.find('Common') == None :
        if not node.find('Common').find('Summary') == None :
            element_summary = node.find('Common').find('Summary').text.strip()

    return (element_id, element_name, element_kind, element_summary)

def read_list_content (element_id, list_content_type, node, list_types, list_elements) :
    list_type_id = element_id + '_' + list_content_type
    list_types.append ( ListType(ID=list_type_id, element=element_id, content_type=list_content_type, num_elements=len(node)) )
    count = 0
    for li in node :
        count = count + 1
        li_content = li_href = li_embed = li_text = None
        if not li.text == None:
            li_content = li.text.strip()
        if 'href' in li.attrib :
            li_href = li.attrib['href']
        if 'embed' in li.attrib :
            li_embed = li.attrib['embed']
        if 'text' in li.attrib :
            li_text = li.attrib['text']
        list_elements.append ( LI(ListID=list_type_id, order=count, content=li_content, href=li_href, embed=li_embed, text=li_text) )

def read_common_content (element_id, node, list_types, list_elements) :
    common_content_tags = ['Citations', 'ExternalLinks', 'Images', 'Videos', 'Maps', 'Feeds']
    for tag in common_content_tags :
        if not node.find(tag) == None:
            read_list_content (element_id, tag.upper(), node.find(tag), list_types, list_elements)
        
def create_crisis_element (node) :

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

    return (crisis_id, new_model, list_types, list_elements)

def create_org_element (node) :

    (org_id, org_name, org_kind, org_summary) = read_wcdb_model (node)

    org_location = None
    if not node.find('Location') == None :
        org_location = node.find('Location').text.strip()

    new_model = Organization (ID=org_id, name=org_name, location=org_location, kind=org_kind, summary=org_summary)

    list_types = []
    list_elements = []

    if not node.find('History') == None:
        read_list_content (org_id, 'HISTORY', node.find('History'), list_types, list_elements)

    if not node.find('Contact') == None:
        read_list_content (org_id, 'CONTACT', node.find('Contact'), list_types, list_elements)
        
    if not node.find('Common') == None:
        read_common_content (org_id, node.find('Common'), list_types, list_elements)

    return (org_id, new_model, list_types, list_elements)

def create_person_element (node) :

    (person_id, person_name, person_kind, person_summary) = read_wcdb_model (node)

    person_location = None
    if not node.find('Location') == None:
        person_location = node.find('Location').text.strip()

    new_model = Person (ID=person_id, name=person_name, location=person_location, kind=person_kind, summary=person_summary)

    list_types = []
    list_elements = []

    if not node.find('Common') == None:
        read_common_content (person_id, node.find('Common'), list_types, list_elements)

    return (person_id, new_model, list_types, list_elements)

