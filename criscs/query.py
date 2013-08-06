import sqlite3


conn = sqlite3.connect('sqlite3.db') # Open connection to the database
c = conn.cursor() 

# All queries go here. Copy paste from queries.sql in the root. Must be raw strings. Add ALL queries
str_query = [
r'SELECT WE.ID, WE.name, LIT.num_elements FROM crises_wcdbelement as WE LEFT JOIN crises_listtype AS LIT ON WE.ID == LIT.element WHERE num_elements >= 2 AND LIT.ID like "%CRI_%" AND content_type == "EXTERNALLINKS"', 
r'SELECT WE.name,SUM(CASE WHEN content_type == "VIDEOS" THEN num_elements ELSE 0 END) AS videos, SUM(CASE WHEN content_type == "IMAGES" THEN num_elements ELSE 0 END) AS images, SUM(CASE WHEN content_type == "CITATIONS" THEN num_elements ELSE 0 END) AS citations  FROM crises_listtype AS LI LEFT JOIN crises_wcdbelement AS WE ON LI.element == WE.ID WHERE LI.ID LIKE "%CRI_%" GROUP BY element',
r'SELECT * FROM (SELECT WE.name, SUM(CASE WHEN LI.content_type == "LOCATIONS" THEN num_elements ELSE 0 END) AS locations FROM crises_listtype AS LI LEFT JOIN crises_wcdbelement AS WE ON LI.element = WE.ID WHERE LI.ID like "%CRI_%" AND num_elements >= 2 GROUP BY element) AS a WHERE a.locations >=2 ;',
r'SELECT b.name AS org_name, link_count  FROM (SELECT org, COUNT(*) AS link_count  FROM crises_r_crisis_org GROUP BY org ORDER BY link_count DESC) AS a LEFT JOIN crises_wcdbelement AS b ON a.org == b.ID  WHERE link_count = (SELECT MAX(link_count) FROM (SELECT org, COUNT(*) AS link_count  FROM crises_r_crisis_org GROUP BY org ORDER BY link_count DESC));',
r'SELECT D.name, D.kind, A.date, C.content  FROM crises_crisis AS A INNER JOIN crises_listtype AS B ON A.wcdbelement_ptr_id == B.element INNER JOIN crises_li AS C on B.ID == C.ListID LEFT JOIN crises_wcdbelement AS D on B.element == D.ID WHERE A.date > "2001-12-31" AND B.content_type == "ECONOMICIMPACT" AND (D.kind LIKE "%Natural%" OR D.kind LIKE "%natural%") ;'
]

# The questions go here. Copy-paste from queries.sql
prashn = [
r'1.Show all crises with 2 or more external links.',
r'2. Show the counts of videos, images and citations for each crisis.', 
r'3.Show the names of crises which have more than one location, with the count of locations.',
r'4.Show the name, id and summary for organization(s) that is(are) associated with maximum number of crises.',
r'5.Show the name and economic impact of natural disasters occuring after 2001.'
]

"""
n = len(str_query)
for i in range(0, n):
	print prashn[i]
	c.execute(str_query[i])
	print c.fetchall()
"""

# This returns the question text
def get_question(q_id):
	return prashn[q_id]

#This returns the query as a string
def get_query(q_id):
	return str_query[q_id]

# This returns the results of the query
def get_query_results(q_id):
	c.execute(str_query[q_id])
	col_names = tuple(map(lambda x: x[0], c.description))
	tmp_list = c.fetchall()
	return [col_names,tmp_list]

#Fill out the function below. All of the functions go into views.py
def query_view(q_id):

	pages = get_all_elems()
	
	html_title = render('title.html', {'title' : 'World Crises Database: ' + 'SQL Queries' } ) #Write code for html_common below.
    
	question = get_question(q_id)
	
	query  = get_query(q_id)

	results = get_query_results(q_id)
	
	final_html = wrap_html(html_title, render('query.html', {'question' : question, 'query':query, 'results':results, 'pages':pages, }))

	return HttpResponse(final_html)
