from django.http import HttpResponse, HttpResponseNotFound, Http404
from crises.models import Crisis, Person, Organization, WCDBElement, ListType, LI, R_Crisis_Person, R_Crisis_Org, R_Org_Person

# Create your views here.
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
    except Http404, e :
        return HttpResponseNotFound('<h1>Page not found</h1>')

def get_title (title, page_type) :
    return '<title>World Crises Database: ' + page_type + ': ' + title + '</title>'

def get_header (name) :
    return '<h1>' + name + '</h1>'

def get_top_content (b) :
    summary = ''
    if not summary == None :
        summary = '<p>' + b.summary + '</p>'
    table = '<table>'
    if not b.kind == None :
        table += '<tr><td>Kind</td><td>' + b.kind + '</td></tr>'
    return (summary, table)

def wcdb_common_view (view_id, page_type) :
    b = WCDBElement.objects.get (pk=view_id)
    html_title = get_title (b.name, page_type)
    html_header = get_header (b.name)

    (summary, top_table) = get_top_content (b)

    return (html_title, html_header, summary, top_table)

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
    html_sections = []
    (html_title, html_header, summary, top_table) = wcdb_common_view (view_id, 'Crisis')
    
    c = Crisis.objects.get (pk=view_id)
    if not c.date == None :
        top_table += '<tr><td>Date</td><td>' + str(c.date) + '</td></tr>'
    if not c.time == None :
        top_table += '<tr><td>Time</td><td>' + str(c.time) + '</td></tr>'
    top_table += '</table>'

    html_sections.append (html_header + summary + top_table)
    
    html_sections.append ( get_crisis_details (view_id) )

    html_sections.append ( get_media (view_id) )

    final_html = '<html>'
    for section in html_sections :
        final_html += section
    final_html += '</html>'
    return HttpResponse (final_html)


def org_view (view_id) :
    html_sections = []
    (html_title, html_header, summary, top_table) = wcdb_common_view (view_id, 'Organization')
    
    c = Organization.objects.get (pk=view_id)
    if not c.location == None :
        top_table += '<tr><td>Date</td><td>' + c.location + '</td></tr>'
    top_table += '</table>'

    html_sections.append (html_header + summary + top_table)
    
    html_sections.append ( get_org_details (view_id) )

    html_sections.append ( get_media (view_id) )

    final_html = '<html>'
    for section in html_sections :
        final_html += section
    final_html += '</html>'
    return HttpResponse (final_html)

def person_view (view_id) :
    html_sections = []
    (html_title, html_header, summary, top_table) = wcdb_common_view (view_id, 'Person')
    
    c = Organization.objects.get (pk=view_id)
    if not c.location == None :
        top_table += '<tr><td>Date</td><td>' + c.location + '</td></tr>'
    top_table += '</table>'

    html_sections.append (html_header + summary + top_table)
    
    html_sections.append ( get_media (view_id) )

    final_html = '<html>'
    for section in html_sections :
        final_html += section
    final_html += '</html>'
    return HttpResponse (final_html)

