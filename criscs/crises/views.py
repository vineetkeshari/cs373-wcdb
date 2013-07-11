from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from crises.models import Crisis, Person, Organization, WCDBElement, ListType, LI, R_Crisis_Person, R_Crisis_Org, R_Org_Person, XMLFile
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
        li.save()

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
    xml_files = XMLFile.objects.all()
    xml = open (str(xml_files[len(xml_files)-1].xml_file), 'r')
    content = sub ('(\s+)', ' ', sub ('<!--(.*)-->', '', xml.read ()) )
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
            return HttpResponseNotFound('<h3>Page not found</h3>')
    except Exception, e :
        return HttpResponseNotFound('<h3>Page not found</h3>' + '<p>' + e.args[0] + '</p>')

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

# This method should return the formatted Citations, External Links, Images, Videos, Maps and Feeds for any WCDBElement
def get_media (view_id) :
    media_dict = {"CITATIONS":[] , "EXTERNALLINKS":[], "IMAGES":[], "VIDEOS":[], "MAPS":[], "FEEDS":[]}
    media_type = media_dict.keys()
    obj = LI.objects.all() # Get all objects from the LI table
    indices = get_indices(view_id, obj, media_dict) # Get indices for each of the Citations, External Links, Images, Videos, Maps and Feeds
    
    media_str = ''
    cite_str = ''
    extlinks_str = ''
    img_str = ''
    vid_str = ''
    maps_str = ''
    feeds_str = ''
    #Extract URL and content for each citation
    for mtype in media_type:
        for index in indices[mtype]:
            if mtype is "CITATIONS" and (indices[mtype] != []) :
                cite_str = cite_str + "<li>" + r'<a href ="' + str(obj[index].href) + r'">' + str(obj[index].content) + '</a>' + "</li>" 

            if mtype is "EXTERNALLINKS" and (indices[mtype] != []) :
                extlinks_str = extlinks_str + "<li>" + r'<a href ="' + str(obj[index].href) + r'">' + str(obj[index].content) + '</a>' + "</li>" 

            if mtype is "IMAGES" and (indices[mtype] != []):
                img_str = img_str + "<td>" + r'<img src ="' + str(obj[index].embed) + r'" alt ="' + str(obj[index].content) + '">' + "</td>"
                #media_str = media_str + img_str 

            if mtype is "VIDEOS" and (indices[mtype] != []):
                vid_str = vid_str + "<td>" + r'<iframe width="420" height="315" src="' + str(obj[index].embed) + r'" frameborder="0" allowfullscreen></iframe>' + "</td>"
                #media_str = media_str + vid_str 

            if mtype is "MAPS" and (indices[mtype] != []):
                maps_str = maps_str + "<li>" + r'<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="' + str(obj[index].embed) + r'"></iframe>' + "</li>"
                #media_str = media_str + maps_str 

            if mtype is "FEEDS" and (indices[mtype] != []):
                feeds_str = feeds_str + "<li>" + r'<a href ="' + str(obj[index].href) + r'">' + str(obj[index].href) + '</a>' + "</li>"
                #media_str = media_str + feeds_str     
    media_str = '<ul>' + cite_str + '</ul>' + '<table>' + '<tr>' + img_str + '</tr>' + '</table>' + '<table>' + '<tr>' + vid_str + '</tr>' + '</table>' +'<ul>' + maps_str + '</ul>' + '<ul>' + feeds_str + '</ul>' + '<ul>' + extlinks_str + '</ul>'
    return media_str

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


# This method should return the formatted Locations, HumanImpact, EconomicImpact, ResourcesNeeded, WaysToHelp items of Crisis
def get_crisis_details (view_id) :
    details_dict = {'LOCATIONS':[], 'HUMANIMPACT':[], 'ECONOMICIMPACT':[], 'RESOURCESNEEDED':[], 'WAYSTOHELP':[]}
    details_list = details_dict.keys()
    obj = LI.objects.all()
    indices = get_indices(view_id, obj, details_dict)
    
    details_str = ''
    #Extract URL and content for each citation
    for mtype in details_list:
        tmp_str = ''
        for index in indices[mtype]:
            if (indices[mtype] != []):
                tmp_str = tmp_str +  "<li>" + r'<a href ="' + str(obj[index].href) + r'">' + str(obj[index].content) + '</a>' + "</li>"
        details_str = details_str + '<ul>' + tmp_str + '</ul>'
    return details_str


# This method should return the formatted History and Contact Info items of Organization
def get_org_details (view_id) :
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
    c_lists = get_crisis_details (view_id)
    html_crisis_content = render ('crisis.html', {'date' : c_date, 'time' : c_time, 'lists' : c_lists, })

    html_media = get_media (view_id)
#    html_media = ''

    html_content = html_common + html_crisis_content + html_media

    final_html = wrap_html (html_title, html_content)

    return HttpResponse (final_html)

