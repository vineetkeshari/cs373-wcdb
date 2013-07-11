from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from crises.models import Crisis, Person, Organization, WCDBElement, ListType, LI, Text_Store, R_Crisis_Person, R_Crisis_Org, R_Org_Person, XMLFile
from crises.forms import DocumentForm

from XMLUtility import process_xml

from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from re import sub
from subprocess import check_output, CalledProcessError, STDOUT

def save_data (all_data) :
    for crisis in all_data['crises'] :
        all_data['crises'][crisis].save()
    for org in all_data['orgs'] :
        all_data['orgs'][org].save()
    for person in all_data['people'] :
        all_data['people'][person].save()
    for list_type in all_data['list_types'] :
        list_type.save()
    for li in all_data['list_elements'] :
        print li.content
        li.save()
    for text in all_data['texts'] :
        text.save()
    for r_co in all_data['rel_crisis_org'] :
        r_co.save()
    for r_cp in all_data['rel_crisis_person'] :
        r_cp.save()
    for r_op in all_data['rel_org_person'] :
        r_op.save()

def import_file (request) :
    # Handle file upload
    if request.method == 'POST' :
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid () :
            try :
                # Check password
                password = request.POST['password']
                if not password == 'baddatamining' :
                    raise Exception('Incorrect Password!')

                # Store the file in the database
                newdoc = XMLFile (xml_file = request.FILES['docfile'])
                newdoc.save ()

                # Validate xml and create models
                uploaded_file = str(newdoc.xml_file)
                all_data = process_xml (uploaded_file)
               
                # Save the data to DB 
                save_data (all_data)

                error = False
                error_string = ''
            except Exception, e :
                error = True
                error_string = str(e)
            # Redirect to the document list after POST
            return render_to_response(
                'crises/templates/upload_success_fail.html',
                {'error': error, 'error_string': error_string},
                context_instance=RequestContext(request),
            )
    else :
        form = DocumentForm() # An empty, unbound form

    # Render list page with the documents and the form
    return render_to_response(
        'crises/templates/import.html',
        {'form': form},
        context_instance=RequestContext(request),
    )


def export_file (request) :
#    xml_files = XMLFile.objects.all()
#    xml = open (str(xml_files[len(xml_files)-1].xml_file), 'r')
#    content = sub ('(\s+)', ' ', sub ('<!--(.*)-->', '', xml.read ()) )
    content = sub ('&', '&amp;', generate_xml ())
    return render_to_response ('crises/templates/export.html', {'text' : content})

def run_tests (request) :
    try :
        unittest_result = check_output(["python","manage.py", "test", "crises"],
                                                    stderr=STDOUT,
        )
        error = False
    except CalledProcessError, cpe :
        error = True
        unittest_result = cpe.output
    return render_to_response ('crises/templates/unittest.html',
                                {'error' : error, 'result' : unittest_result, },
                                context_instance=RequestContext(request),
    )

# Create your views here.
def render (name, data) :
    template = loader.get_template ('crises/templates/' + name)
    context = Context (data)
    return template.render (context)

def wrap_html (html_title, html_content) :
    return '<html><head>' + html_title + '</head><body>' + html_content + '</body></html>'

def index (request) :
    members = ['Ambareesha Nittala', 'Brandon Fairchild', 'Chris Coney', 'Roberto Weller', 'Rogelio Sanchez', 'Vineet Keshari']

    all_wcdb = WCDBElement.objects.all ()
    pages = {}
    pages ['crises'] = []
    pages ['people'] = []
    pages ['orgs'] = []
    for elem in all_wcdb :
        if elem.ID[:3] == 'CRI' :
            pages ['crises'].append ({'name' : elem.name, 'id' : elem.ID})
        if elem.ID[:3] == 'ORG' :
            pages ['orgs'].append ({'name' : elem.name, 'id' : elem.ID})
        if elem.ID[:3] == 'PER' :
            pages ['people'].append ({'name' : elem.name, 'id' : elem.ID})

    return HttpResponse ( render ('index.html', {'members' : members, 'pages' : pages, }))

def base_view (request, view_id) :
    view_type = view_id[:3]
    try :
        if view_type == 'CRI' :
            return crisis_view (view_id)
        elif view_type == 'ORG' :
            return org_view (view_id)
        elif view_type == 'PER' :
            return person_view (view_id)
        else :
            return HttpResponseNotFound('<h1>Page not found</h1>')
    except Exception, e :
        return HttpResponseNotFound('<h1>Page not found</h1>' + '<p>' + e.args[0] + '</p>')

def wcdb_common_view (view_id, page_type) :
    b = WCDBElement.objects.get (pk=view_id)
    summary = kind = ''
    if not summary == None :
        summary = b.summary
    if not b.kind == None :
        kind = b.kind
    html_title = render ('title.html', {'title' : 'World Crises Database: ' + page_type + ': ' + b.name, } )
    html_common = render ('common.html', {'name' : b.name, 'summary' : summary, 'kind' : kind})

    return (html_title, html_common)

def generate_xml () :
    texts = Text_Store.objects.all ()

    generated_xml = 'Your XML has %d elements:\n\n' % len(texts)
    generated_xml += r'<?xml version="1.0" encoding="ISO-8859-1" ?>' + '\n'
    generated_xml += '<WorldCrises>\n'

    for text in texts :
        generated_xml += text.content

    generated_xml += '</WorldCrises>\n'

    return generated_xml

# This method should return the formatted Citations, External Links, Images, Videos, Maps and Feeds for any WCDBElement
def get_media (view_id) :
    media_dict = {"CITATIONS":[] , "EXTERNALLINKS":[], "IMAGES":[], "VIDEOS":[], "MAPS":[], "FEEDS":[]}
    store_dict = {"CITATIONS":[] , "EXTERNALLINKS":[], "IMAGES":[], "VIDEOS":[], "MAPS":[], "FEEDS":[]}
    media_type = media_dict.keys()
    obj = LI.objects.all() # Get all objects from the LI table
    indices = get_indices(view_id, obj, media_dict) # Get indices for each of the Citations, External Links, Images, Videos, Maps and Feeds
    
    
    #Extract URL and content for each citation
    for mtype in media_type:
        for index in indices[mtype]:
            if mtype is "CITATIONS" and (indices[mtype] != []) :
                tmp_list = [str(obj[index].href), str(obj[index].content)]
                store_dict[mtype].append(tmp_list)

            if mtype is "EXTERNALLINKS" and (indices[mtype] != []) :
                tmp_list = [str(obj[index].href), str(obj[index].content)]
                store_dict[mtype].append(tmp_list)

            if mtype is "IMAGES" and (indices[mtype] != []):
                tmp_list = [str(obj[index].embed), str(obj[index].content)]
                store_dict[mtype].append(tmp_list)

            if mtype is "VIDEOS" and (indices[mtype] != []):
                tmp_list = [str(obj[index].embed)]
                store_dict[mtype].append(tmp_list) 

            if mtype is "MAPS" and (indices[mtype] != []):
                tmp_list = [str(obj[index].embed)]
                store_dict[mtype].append(tmp_list) 

            if mtype is "FEEDS" and (indices[mtype] != []):
                ftmp_list = [str(obj[index].href), str(obj[index].href)]
                store_dict[mtype].append(tmp_list)     
    
    return store_dict

def get_indices(view_id, LI_table, media_dict):
    tmp_dict = media_dict 
    tmp_type = media_dict.keys()
    assert type(tmp_dict) is dict
    assert type(tmp_type) is list
    # Store all the indices for the media type
    for i in range(0, len(LI_table)):
        for elem in tmp_type:
            if LI_table[i].ListID == view_id + "_" + elem:
                tmp_dict[elem].append(i)
    return tmp_dict


def get_content_href (obj_index) :
    my_content = None
    if not obj_index.content == None :
        my_content = str(obj_index.content)
    my_href = None
    if not obj_index.href == None :
        my_href = str(obj_index.href)
    return (my_content, my_href)


# This method should return the formatted Locations, HumanImpact, EconomicImpact, ResourcesNeeded, WaysToHelp items of Crisis
def get_crisis_details (view_id) :
    details_dict = {'LOCATIONS':[], 'HUMANIMPACT':[], 'ECONOMICIMPACT':[], 'RESOURCESNEEDED':[], 'WAYSTOHELP':[]}
    store_dict = {'LOCATIONS':[], 'HUMANIMPACT':[], 'ECONOMICIMPACT':[], 'RESOURCESNEEDED':[], 'WAYSTOHELP':[]}
    details_list = details_dict.keys()
    obj = LI.objects.all()
    indices = get_indices(view_id, obj, details_dict)
    
    #Extract URL and content for each citation
    for mtype in details_list:
        for index in indices[mtype]:
            if (indices[mtype] != []):
                (my_content, my_href)  = get_content_href(obj[index])
                tmp_list = [my_href, my_content]
                store_dict[mtype].append(tmp_list)
    return store_dict


# This method should return the formatted History and Contact Info items of Organization
def get_org_details (view_id) :
    #1. Get the org(s) from the view_id, store in dict
    #2. Query LI for the history
    
    return ''
    
# Returns all data associated with the person 
def get_person_details(view_id):
    return ''
    
def crisis_view (view_id) :
    (html_title, html_common) = wcdb_common_view (view_id, 'Crisis')
    
    c = Crisis.objects.get (pk=view_id)
    c_date = c_time = ''
    if not c.date == None :
        c_date = str(c.date)
    if not c.time == None :
        c_time = str(c.time)
    c_lists = get_media (view_id) 
    c_details = get_crisis_details (view_id)

    html_crisis_content = render ('crisis.html', {'date' : c_date, 'time' : c_time, 'lists':c_lists, 'details':c_details,})

    html_media = get_media (view_id)

    html_content = html_crisis_content #+ html_media

    final_html = wrap_html (html_title, html_content)

    return HttpResponse (final_html)

