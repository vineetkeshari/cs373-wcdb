from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from crises.models import Crisis, Person, Organization, WCDBElement, ListType, LI, Text_Store, R_Crisis_Person, R_Crisis_Org, R_Org_Person, XMLFile
from crises.forms import DocumentForm

from XMLUtility import process_xml
from query import query_view, get_all_queries

from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.servers.basehttp import FileWrapper

from re import sub
from subprocess import check_output, CalledProcessError, STDOUT
from os.path import getsize
from django.utils.safestring import mark_safe

is_prod = False
if is_prod :
    prod_dir = '/users/cs373/rosuto82/django.wsgi'
else :
    prod_dir = ''

def test_view (request) :
    """
    DEBUG: Use for quick renders
    """
    http_thing = r'<iframe marginheight="0" marginwidth="0" src="https://maps.google.com/maps?um=1&amp;amp;safe=off&amp;amp;amphl=en&amp;amp;ampq=2011%20Norway%20Attacks&amp;amp;bav=on.2,or.r_cp.r_qf.&amp;amp;bvm=bv.48705608,d.eWU&amp;amp;biw=1600&amp;amp;bih=775&amp;amp;ie=UTF-8&amp;amp;sa=N&amp;amp;tab=il" frameborder="0" height="350" scrolling="no" width="425"></iframe>'
    http_2 = r'<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://maps.google.com/maps?ie=UTF8&amp;ll=30.307761,-97.753401&amp;spn=0.33078,0.060425&amp;t=m&amp;z=10&amp;output=embed"></iframe><br /><small><a href="https://maps.google.com/maps?ie=UTF8&amp;ll=30.307761,-97.753401&amp;spn=0.33078,0.060425&amp;t=m&amp;z=10&amp;source=embed" style="color:#0000FF;text-align:left">View Larger Map</a></small>'
    http_3 = r'<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://maps.google.com/maps?ie=UTF8&amp;ll=30.307761,-97.753401&amp;spn=0.33078,0.060425&amp;t=m&amp;z=10&amp;output=embed"></iframe>'
    return HttpResponse(http_3)

def get_all_elems () :
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
    return pages


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
    for text in all_data['texts'] :
        text.save()
    for r_co in all_data['rel_crisis_org'] :
        r_co.save()
    for r_cp in all_data['rel_crisis_person'] :
        r_cp.save()
    for r_op in all_data['rel_org_person'] :
        r_op.save()

def import_file (request) :
    pages = get_all_elems ()
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
                uploaded_file = 'WCDB_tmp.xml'
                f = open (uploaded_file, 'w')
                for chunk in request.FILES['docfile'].chunks():
                    f.write(chunk)
                f.close()

                # Validate xml and create models
                all_data = process_xml (uploaded_file, False)
               
                # Save the data to DB 
                save_data (all_data)

                error = False
                error_string = ''
            except Exception, e :
                error = True
                error_string = str(e)
            # Redirect after POST
            return render_to_response(
                'upload_success_fail.html',
                {'error': error, 'error_string': error_string, 'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir,},
                context_instance=RequestContext(request),
            )
    else :
        form = DocumentForm() # An empty, unbound form

    # Render the form
    return render_to_response(
        'import.html',
        {'form': form, 'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir},
        context_instance=RequestContext(request),
    )

def merge_import_file (request) :
    pages = get_all_elems ()
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
                uploaded_file = 'WCDB_merge_tmp.xml'
                f = open (uploaded_file, 'w')
                for chunk in request.FILES['docfile'].chunks():
                    f.write(chunk)
                f.close()

                # Validate xml and create models
                all_data = process_xml (uploaded_file, True)
               
                # Save the data to DB 
                save_data (all_data)

                error = False
                error_string = ''
            except Exception, e :
                error = True
                error_string = str(e)
            # Redirect after POST
            return render_to_response(
                'upload_success_fail.html',
                {'error': error, 'error_string': error_string, 'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir,},
                context_instance=RequestContext(request),
            )
    else :
        form = DocumentForm() # An empty, unbound form

    # Render the form
    return render_to_response(
        'merge_import.html',
        {'form': form, 'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir},
        context_instance=RequestContext(request),
    )

def export_file (request) :
    content = sub ('&', '&amp;', generate_xml ())

    filename = 'WCDB_CrisCS_export.xml'                                
    export_file = File (open (filename, 'w'))
    export_file.write (content.encode('ascii', 'xmlcharrefreplace'))
    export_file.close()

    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/force-download')
    response['Content-Disposition'] = 'attachment; filename="WCDB-CrisCS.xml"'
    response['Content-Length'] = getsize(filename)
    return response

def run_tests (request) :
    pages = get_all_elems ()
    try :
        unittest_result = check_output(["python","manage.py", "test", "crises"],
                                                    stderr=STDOUT,
        )
        error = False
    except CalledProcessError, cpe :
        error = True
        unittest_result = cpe.output
    return render_to_response ('unittest.html',
                                {'error' : error, 'result' : unittest_result, 'pages' : pages, 'is_prod':is_prod, 'prod_dir':prod_dir},
                                context_instance=RequestContext(request),
    )

# Create your views here.
def render (name, data) :
    template = loader.get_template (name)
    context = Context (dict(data.items() + {'is_prod':is_prod, 'prod_dir':prod_dir}.items()))
    return template.render (context)

def wrap_html (html_title, html_content) :
    return '<html><head>' + html_title + '</head><body>' + html_content + '</body></html>'

def index (request) :
    members = ['Ambareesha Nittala', 'Brandon Fairchild', 'Chris Coney', 'Roberto Weller', 'Rogelio Sanchez', 'Vineet Keshari']

    pages = get_all_elems ()

    return render_to_response(
        'index.html',
        {'members': members, 'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir},
        context_instance=RequestContext(request),
    )

def search_result_helper(needle, haystack) :
    if (needle is None or haystack is None) :
        return False
    
    needle = needle.lower().strip()
    haystack = haystack.lower().strip()

    if needle in haystack :
        location = haystack.find(needle)
        size = len(needle)
        found = "<strong>" + haystack[location:location+size] + "</strong>"
        return haystack[location-15:location] + found + haystack[location+size:location+size+15]
    else :
        return False

def search_in_wcdb_element(query, wcdb) :
    find_result = search_result_helper(query, wcdb.name)
    if (find_result is not False) :
        return [wcdb.name, wcdb.ID, find_result]

    find_result = search_result_helper(query, wcdb.summary)
    if (find_result is not False) :
        return [wcdb.name, wcdb.ID, find_result]

    return False

def search_results (request) :
    results = []
    if request.method == 'GET' and ('query' in request.GET) :
        if len(request.GET['query']) > 0 :
            #Had a search query
            query = request.GET['query']
             
            all_wcdb = WCDBElement.objects.all ()
            for wcdb in all_wcdb :
                query_result = []
                for word in query.split():
                    result = search_in_wcdb_element(word, wcdb)
                    if (result is not False) :
                        query_result.append(result[2])
                if query_result is not None and len(query_result) > 0:
                    results.append([wcdb.ID, query_result, wcdb.name])
                    
        else :
            #Query was blank
            results.append("Please enter a query")

    #Sort results on number of hits
    results.sort(key = lambda s: len(s[1]))
    results.reverse()

    pages = get_all_elems ()
    return render_to_response(
        'search_results.html',
        {'query': query, 'results': results, 'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir},
        context_instance=RequestContext(request),
    )    

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
            return HttpResponseNotFound('<h5>Page not found</h5>')
    except Exception, e :
        return HttpResponseNotFound('<h5>Page not found</h5>' + '<p>' + e + '</p>')

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

    generated_xml = ''
    #generated_xml += 'Your XML has %d elements:\n\n' % len(texts)
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
                tmp_list = [sub('&amp;','&',str(obj[index].embed))]
                store_dict[mtype].append(tmp_list) 

            if mtype is "FEEDS" and (indices[mtype] != []):
                tmp_list = [str(obj[index].embed), str(obj[index].embed)]
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


def get_cop_details(view_id):
    if view_id[:3] == "CRI":
        org_dict = get_org_names_cris(view_id)
        pers_dict = get_person_names_cris(view_id)
        return [org_dict, pers_dict]

    elif view_id[:3] == "ORG":
        cris_dict = get_crises_names_orgs(view_id)
        pers_dict = get_person_names_orgs(view_id)
        return [cris_dict, pers_dict]

    elif view_id[:3] == "PER":
        cris_dict = get_crises_names_pers(view_id)
        org_dict = get_org_names_pers(view_id)
        return [cris_dict, org_dict]
    else :
        return None


def get_org_names_cris(view_id):
    obj = R_Crisis_Org.objects.all()
    orgs = []
    # Get orgs corresponding to the view_id
    for i in range(0, len(obj)):
        if obj[i].crisis == view_id:
            orgs.append(obj[i].org)

    orgs = list(set(orgs)) # Retain only unique items
    final_list= []
    obj_2 = WCDBElement.objects.all()

    for i in range(0, len(obj_2)):
        for org in orgs:
            if obj_2[i].ID == org:
                tmp_list = [org, str(obj_2[i].name)]
                final_list.append(tmp_list)

    return final_list

def get_org_names_pers(view_id):
    obj = R_Org_Person.objects.all()
    orgs = []
    for i in range(0, len(obj)):
        if obj[i].person == view_id:
            orgs.append(obj[i].org)

    orgs = list(set(orgs)) # Retain only unique items
    final_list =[]
    obj_2 = WCDBElement.objects.all()

    for i in range(0, len(obj_2)):
        for org in orgs:
            if obj_2[i].ID == org:
                tmp_list = [org, str(obj_2[i].name)]
                final_list.append(tmp_list)
                

    return final_list

def get_person_names_cris(view_id):
    obj = R_Crisis_Person.objects.all()
    pers = []
    for i in range(0, len(obj)):
        if obj[i].crisis == view_id:
            pers.append(obj[i].person)

    pers = list(set(pers))
    final_list = []
    obj_2 = WCDBElement.objects.all()

    for i in range(0, len(obj_2)):
        for person in pers:
            if obj_2[i].ID == person:
                tmp_list = [person, str(obj_2[i].name)]
                final_list.append(tmp_list)
    return final_list

def get_person_names_orgs(view_id):
    obj = R_Org_Person.objects.all()
    pers = []
    for i in range(0, len(obj)):
        if obj[i].org == view_id:
            pers.append(obj[i].person)

    pers = list(set(pers))
    final_list = []
    obj_2 = WCDBElement.objects.all()

    for i in range(0, len(obj_2)):
        for person in pers:
            if obj_2[i].ID == person:
                tmp_list = [person, str(obj_2[i].name)]
                final_list.append(tmp_list)
    return final_list

def get_crises_names_orgs(view_id):
    obj = R_Crisis_Org.objects.all()
    crises = []
    for i in range(0, len(obj)):
        if obj[i].org == view_id:
            crises.append(obj[i].crisis)

    crises = list(set(crises))
    final_list = []
    obj_2 = WCDBElement.objects.all()

    for i in range(0, len(obj_2)):
        for crisis in crises:
            if obj_2[i].ID == crisis:
                tmp_list = [crisis, str(obj_2[i].name)]
                final_list.append(tmp_list)
    
    return final_list

def get_crises_names_pers(view_id):
    obj = R_Crisis_Person.objects.all()
    crises = []
    for i in range(0, len(obj)):
        if obj[i].person == view_id:
            crises.append(obj[i].crisis)

    crises = list(set(crises))
    final_list = []
    obj_2 = WCDBElement.objects.all()

    for i in range(0, len(obj_2)):
        for crisis in crises:
            if obj_2[i].ID == crisis:
                tmp_list = [crisis, str(obj_2[i].name)]
                final_list.append(tmp_list)
    
    return final_list




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
    obj = R_Crisis_Org.objects.all()
    obj_2 = LI.objects.all()
    orgs = ['history', 'contact'] # Retain only unique items
    cntct = ['content', 'href']
    cntct_org = dict.fromkeys(cntct)
    dict_org = dict.fromkeys(orgs)
    dict_org['contact'] = []
    
    for i in range(0, len(obj_2)):
        if obj_2[i].ListID == view_id + "_" + "HISTORY":
            dict_org['history'] = [obj_2[i].content]

    for i in range(0, len(obj_2)):
        if obj_2[i].ListID == view_id + "_" + "CONTACTINFO":
            tmp_list = [obj_2[i].content, obj_2[i].href]
            dict_org['contact'].append(tmp_list)

    return dict_org

# Returns all data associated with the person 

def get_name_kind_summary(view_id):
    obj = WCDBElement.objects.all()
    nks_dict = {'name':[], 'kind':[], 'summary':[] }
    for i in range(0, len(obj)):
        if obj[i].ID == view_id:
            nks_dict['name'].append(obj[i].name)
            nks_dict['kind'].append(obj[i].kind)
            nks_dict['summary'].append(obj[i].summary)
    return nks_dict
        

def get_location(view_id):
    location = ''
    if view_id[:3] == "PER":
        obj = Person.objects.all()
        for i in range(0, len(obj)):
            if obj[i].wcdbelement_ptr_id == view_id:
                location = location + str(obj[i].location)
    if view_id[:3] == "ORG":
        obj = Organization.objects.all()
        for i in range(0, len(obj)):
            if obj[i].wcdbelement_ptr_id == view_id:
                location = location + str(obj[i].location)
    return location

def crisis_view (view_id) :
    (html_title, html_common) = wcdb_common_view (view_id, 'Crisis')

    pages = get_all_elems()
    nks_dict = get_name_kind_summary(view_id)
    
    c = Crisis.objects.get (pk=view_id)
    c_date = c_time = 'Unspecified'
    if not c.date == None :
        c_date = str(c.date)
    if not c.time == None :
        c_time = str(c.time)

    c_lists = get_media (view_id) 
    c_details = get_crisis_details (view_id)
    c_orgs = get_cop_details(view_id)[0]
    c_persons = get_cop_details(view_id)[1]

    html_crisis_content = render ('crisis.html', {'date' : c_date, 'time' : c_time, 'lists':c_lists, 'details':c_details, 'orgs':c_orgs, 'person':c_persons, 'pages':pages, 'nks':nks_dict,})

    html_media = get_media (view_id)

    html_content = html_crisis_content #+ html_media

    final_html = wrap_html (html_title, html_content)

    return HttpResponse (final_html)


def org_view(view_id):

    pages = get_all_elems()
    nks_dict = get_name_kind_summary(view_id)

    (html_title, html_common) = wcdb_common_view (view_id, 'Organization')
    
    org_location = get_location(view_id)
    
    org_lists = get_media(view_id) 
    
    org_details = get_org_details (view_id)

    org_crises = get_cop_details(view_id)[0]
    org_persons = get_cop_details(view_id)[1]

    html_crisis_content = render ('organizations.html', {'lists':org_lists, 'details':org_details, 'crises':org_crises,  'person':org_persons, 'pages':pages, 'nks':nks_dict, 'location':org_location,})

    html_content = html_crisis_content #+ html_media

    final_html = wrap_html (html_title, html_content)

    return HttpResponse (final_html)


def person_view(view_id):

    pages = get_all_elems()
    nks_dict = get_name_kind_summary(view_id)

    (html_title, html_common) = wcdb_common_view (view_id, 'Person')
    
    per_location = get_location(view_id)
    
    per_lists = get_media(view_id) 
    

    per_crises = get_cop_details(view_id)[0]
    per_orgs = get_cop_details(view_id)[1]

    html_crisis_content = render ('persons.html', {'lists':per_lists, 'crises':per_crises, 'orgs':per_orgs, 'pages':pages, 'nks':nks_dict, 'location':per_location,})

    html_content = html_crisis_content #+ html_media

    final_html = wrap_html (html_title, html_content)

    return HttpResponse (final_html)

def mcrises (request) :

    pages = get_all_elems ()

    return render_to_response(
        'morecrises.html',
        {'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir},
        context_instance=RequestContext(request),
    )

def morganizations (request) :

    pages = get_all_elems ()

    return render_to_response(
        'moreorganizations.html',
        {'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir},
        context_instance=RequestContext(request),
    )

def mpeople (request) :

    pages = get_all_elems ()

    return render_to_response(
        'morepeople.html',
        {'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir},
        context_instance=RequestContext(request),
    )

def query_view_wrapper (request, q_id) :

    pages = get_all_elems ()
    (question, query, results, q_id) = query_view (q_id)

    return render_to_response(
        'query.html',
        {'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir, 'question' : question, 'query':query, 'results':results, 'q_id':q_id+1,},
        context_instance=RequestContext(request),
    )

def list_queries (request) :
    pages = get_all_elems ()
    queries = get_all_queries()

    return render_to_response(
        'queries_page.html',
        {'pages': pages, 'is_prod':is_prod, 'prod_dir':prod_dir, 'queries':queries},
        context_instance=RequestContext(request),
    )
