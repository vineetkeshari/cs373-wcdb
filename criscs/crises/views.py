from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from crises.models import Crisis, Person, Organization, WCDBElement, ListType, LI, R_Crisis_Person, R_Crisis_Org, R_Org_Person, XMLFile
from crises.forms import DocumentForm

from XMLUtility import process_xml

from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

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
#            try :
                # Validate xml and create models
                uploaded_file = request.FILES['docfile'].read()
                all_data = process_xml (uploaded_file)
               
                # Save the data to DB 
                save_data (all_data)

                # Store the file in the database
                newdoc = XMLFile (xml_file = request.FILES['docfile'])
                newdoc.save ()
                error = False
                error_string = ''

#            except Exception, e :
#                error = True
#                error_string = str(e)
#                raise e
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
    xml_file = XMLFile.objects.all() [0]
    return HttpResponseRedirect ('/' + xml_file.xml_file.url)

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
    print pages['crises']
    print pages['orgs']
    print pages['people']


    return HttpResponse ( render ('index.html', {'members' : members, 'pages' : pages, }))

def base_view (request, view_id) :
        view_type = view_id[:3]
#    try :
        if view_type == 'CRI' :
            return crisis_view (view_id)
        elif view_type == 'ORG' :
            return org_view (view_id)
        elif view_type == 'PER' :
            return person_view (view_id)
        else :
            return HttpResponseNotFound('<h1>Page not found</h1>')
#    except Exception, e :
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

# This method should return the formatted Citations, External Links, Images, Videos, Maps and Feeds for any WCDBElement
def get_media (view_id) :
    media_type = ["CITATIONS", "EXTERNALLINKS", "IMAGES", "VIDEOS", "MAPS", "FEEDS"]
    obj = LI.objects.all() # Get all objects from the LI table
    indices = get_indices_media(view_id, obj) # Get indices for each of the Citations, External Links, Images, Videos, Maps and Feeds
    
    media_str = ''
    #Extract URL and content for each citation
    for mtype in media_type:
        for index in indices[mtype]:
            if mtype in ["CITATIONS", "EXTERNALLINKS"] and (indices[mtype] != []) :
                cite_str = "<li>" + r'<a href ="' + obj[index].href + r'">' + obj[index].content + '</a>' + "</li>"
                media_str = media_str + cite_str 

            if mtype is "IMAGES" and (indices[mtype] != []):
                img_str = "<li>" + r'<img src ="' + obj[index].embed + r'" alt ="' + obj[index].content + '">' + "</li>"
                media_str = media_str + img_str 

            if mtype is "VIDEOS" and (indices[mtype] != []):
                vid_str = "<li>" + r'<iframe width="420" height="315" src="' + obj[index].embed + r'" frameborder="0" allowfullscreen></iframe>' + "</li>"
                media_str = media_str + vid_str 

            if mtype is "MAPS" and (indices[mtype] != []):
                maps_str = "<li>" + r'<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="' + obj[index].embed + r'"></iframe>' + "</li>"
                media_str = media_str + maps_str 

            if mtype is "FEEDS" and (indices[mtype] != []):
                feeds_str = "<li>" + r'<a href ="' + obj[index].href + r'">' + obj[index].href + '</a>' + "</li>"
                media_str = media_str + feeds_str 
    
        
    media_str = '<ul>' + media_str + '</ul>'
    return media_str

def get_indices_media(view_id, LI_table):
    media_dict = {"CITATIONS":[] , "EXTERNALLINKS":[], "IMAGES":[], "VIDEOS":[], "MAPS":[], "FEEDS":[]}
    media_type = ["CITATIONS", "EXTERNALLINKS", "IMAGES", "VIDEOS", "MAPS", "FEEDS"]
    # Store all the indices for the media type
    for i in range(0, len(LI_table)):
        if LI_table[i].ListID.ID == view_id + "_" + media_type[0]:
            media_dict['CITATIONS'].append(i)
        if LI_table[i].ListID.ID == view_id + "_" + media_type[1]:
            media_dict['EXTERNALLINKS'].append(i)
        if LI_table[i].ListID.ID == view_id + "_" + media_type[2]:
            media_dict['IMAGES'].append(i)
        if LI_table[i].ListID.ID == view_id + "_" + media_type[3]:
            media_dict['VIDEOS'].append(i)
        if LI_table[i].ListID.ID == view_id + "_" + media_type[4]:
            media_dict['MAPS'].append(i)
        if LI_table[i].ListID.ID == view_id + "_" + media_type[5]:
            media_dict['FEEDS'].append(i)
    return media_dict


# This method should return the formatted Locations, HumanImpact, EconomicImpact, ResourcesNeeded, WaysToHelp items of Crisis
def get_crisis_details (view_id) :
    return ''

# This method should return the formatted History and Contact Info items of Organization
def get_org_details (view_id) :
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

#    html_media = get_media (view_id)
    html_media = ''

    html_content = html_common + html_crisis_content + html_media

    final_html = wrap_html (html_title, html_content)

    print final_html
    return HttpResponse (final_html)

