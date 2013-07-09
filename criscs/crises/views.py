from django.http import HttpResponse, HttpResponseNotFound
from django.template import Context, loader
from crises.models import Crisis, Person, Organization, WCDBElement, ListType, LI, R_Crisis_Person, R_Crisis_Org, R_Org_Person

# Create your views here.
def render (name, data) :
    template = loader.get_template ('crises/templates/' + name)
    context = Context (data)
    return template.render (context)

def wrap_html (html_title, html_content) :
    return '<html><head>' + html_title + '</head><body>' + html_content + '</body></html>'

def index (request) :
    members = ['Ambarish Nittala', 'Brandon Fairchild', 'Chris Coney', 'Roberto Weller', 'Rogelio Sanchez', 'Vineet Keshari']

    all_wcdb = WCDBElement.objects.all ()
    pages = {}
    pages ['crises'] = []
    pages ['people'] = []
    pages ['orgs'] = []
    for elem in all_wcdb :
        if elem.ID[:3] == 'CRI' :
            pages ['crises'].append ({elem.name : elem.ID})
        if elem.ID[:3] == 'ORG' :
            pages ['orgs'].append ({elem.name : elem.ID})
        if elem.ID[:3] == 'PER' :
            pages ['people'].append ({elem.name : elem.ID})

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

# This method should return the formatted Citations, External Links, Images, Videos, Maps and Feeds for any WCDBElement
def get_media (view_id) :
    return ''

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

    html_media = get_media (view_id)

    html_content = html_common + html_crisis_content + html_media

    final_html = wrap_html (html_title, html_content)

    print final_html
    return HttpResponse (final_html)

