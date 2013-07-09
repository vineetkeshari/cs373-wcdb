from crises.models import WCDBElement, Crisis, Organization, Person, ListType, LI, R_Crisis_Person, R_Crisis_Org, R_Org_Person

def read_wcdb_model (node) :
    assert 'ID' in node.attrib
    assert 'Name' in node.attrib
    element_id = node.attrib['ID']
    element_name = node.attrib['Name']
    
    assert WCDBElement.objects.get (pk=element_id) == None

    element_kind = None
    if 'Kind' in node :
        element_kind = node['Kind'].text.strip()
    
    element_summary = None
    if 'Summary' in node :
        element_summary = node['Summary'].text.strip()

    return (element_id, element_name, element_kind, element_summary)

def read_list_content (element_id, list_content_type, node, list_types, list_elements) :
    list_type_id = element_id + '_' + list_content_type
    list_types.append ( ListType(ID=list_type_id, element=element_id, content_type=list_content_type, num_elements=len(node)) )
    count = 0
    for li in node :
        count = count + 1
        li_content = li_href = li_embed = li_text = None
        if not node[li].text.strip() == '':
            li_content = node[li].text.strip()
        if 'href' in node[li].attrib :
            li_href = node[li].attrib['href']
        if 'embed' in node[li].attrib :
            li_embed = node[li].attrib['embed']
        if 'text' in node[li].attrib :
            li_text = node[li].attrib['text']
        list_elements.append ( ListElement(ListID=list_type_id, order=count, content=li_content, href=li_href, embed=li_embed, text=li_text) )

def read_common_content (element_id, node, list_types, list_elements) :
    if 'Citations' in node:
        read_list_content (element_id, 'CITATIONS', node['Citations'], list_types, list_elements)
        
    if 'ExternalLinks' in node:
        read_list_content (element_id, 'EXTERNALLINKS', node['ExternalLinks'], list_types, list_elements)
        
    if 'Images' in node:
        read_list_content (element_id, 'IMAGES', node['Images'], list_types, list_elements)
        
    if 'Videos' in node:
        read_list_content (element_id, 'VIDEOS', node['Videos'], list_types, list_elements)
        
    if 'Maps' in node:
        read_list_content (element_id, 'MAPS', node['Maps'], list_types, list_elements)
        
    if 'Feeds' in node:
        read_list_content (element_id, 'FEEDS', node['Feeds'], list_types, list_elements)

def create_crisis_element (node) :

    (crisis_id, crisis_name, crisis_kind, crisis_summary) = read_wcdb_model (node)

    if 'Date' in node :
        crisis_date = node['Date'].text.strip()

    if 'Time' in node :
        crisis_time = node['Time'].text.strip()

    new_model = Crisis (ID=crisis_id, name=crisis_name, date=crisis_date, time=crisis_time, kind=crisis_kind, summary=crisis_summary)

    list_types = []
    list_elements = []

    if 'Locations' in node :
        read_list_content (crisis_id, 'LOCATIONS', node['Locations'], list_types, list_elements)

    if 'HumanImpact' in node:
        read_list_content (crisis_id, 'HUMANIMPACT', node['HumanImpact'], list_types, list_elements)
        
    if 'EconomicImpact' in node:
        read_list_content (crisis_id, 'ECONOMICIMPACT', node['EconomicImpact'], list_types, list_elements)
        
    if 'ResourcesNeeded' in node:
        read_list_content (crisis_id, 'RESOURCESNEEDED', node['ResourcesNeeded'], list_types, list_elements)
        
    if 'WaysToHelp' in node:
        read_list_content (crisis_id, 'WAYSTOHELP', node['WaysToHelp'], list_types, list_elements)
        
    if 'Common' in node:
        read_common_content (crisis_id, node['Common'], list_types, list_elements)

    return (crisis_id, new_model, list_types, list_elements)

def create_org_element (node) :

    (org_id, org_name, org_kind, org_summary) = read_wcdb_model (node)

    if 'Location' in node :
        org_location = node['Location'].text.strip()

    new_model = Organization (ID=org_id, name=org_name, location=org_location, kind=org_kind, summary=org_summary)

    list_types = []
    list_elements = []

    if 'History' in node :
        read_list_content (org_id, 'HISTORY', node['History'], list_types, list_elements)

    if 'Contact' in node:
        read_list_content (org_id, 'CONTACT', node['Contact'], list_types, list_elements)
        
    return (org_id, new_model, list_types, list_elements)

def create_person_element (node) :

    (person_id, person_name, person_kind, person_summary) = read_wcdb_model (node)

    if 'Location' in node :
        person_location = node['Location'].text.strip()

    new_model = Person (ID=person_id, name=person_name, location=person_location, kind=person_kind, summary=person_summary)

    list_types = []
    list_elements = []

    return (person_id, new_model, list_types, list_elements)

