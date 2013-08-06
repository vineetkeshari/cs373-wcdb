SELECT "1.Show all crises with 2 or more external links."

SELECT 
WE.ID, 
WE.name, 
LIT.num_elements 
FROM crises_wcdbelement as WE LEFT JOIN crises_listtype AS LIT ON WE.ID == LIT.element 
WHERE num_elements >= 2 AND LIT.ID like "%CRI_%" AND content_type == "EXTERNALLINKS"

SELECT "2. Show the counts of videos, images and citations for each crisis."

SELECT
WE.name,
SUM(CASE WHEN content_type == "VIDEOS" THEN num_elements ELSE 0 END) AS videos, 
SUM(CASE WHEN content_type == "IMAGES" THEN num_elements ELSE 0 END) AS images, 
SUM(CASE WHEN content_type == "CITATIONS" THEN num_elements ELSE 0 END) AS citations  
FROM crises_listtype AS LI LEFT JOIN crises_wcdbelement AS WE ON LI.element == WE.ID  
WHERE LI.ID LIKE "%CRI_%" GROUP BY element;

SELECT "3.Show the names of crises which have more than one location, with the count of locations."

SELECT
* 
FROM 

(SELECT WE.name, SUM(CASE WHEN LI.content_type == "LOCATIONS" THEN num_elements ELSE 0 END) AS locations FROM crises_listtype AS LI LEFT JOIN crises_wcdbelement AS WE ON LI.element = WE.ID WHERE LI.ID like "%CRI_%" AND num_elements >= 2 GROUP BY element) AS a 

WHERE a.locations >=2 ;

SELECT "4.Show the name, id and summary for organization(s) that is(are) associated with maximum number of crises."

SELECT 
b.name AS org_name, 
link_count  
FROM (SELECT org, COUNT(*) AS link_count  FROM crises_r_crisis_org GROUP BY org ORDER BY link_count DESC) AS a 
LEFT JOIN crises_wcdbelement AS b ON a.org == b.ID  
WHERE link_count = 
(
SELECT MAX(link_count) FROM (SELECT org, COUNT(*) AS link_count  FROM crises_r_crisis_org GROUP BY org ORDER BY link_count DESC)
);


SELECT "5.Show the name and economic impact of natural disasters occuring after 2001."

SELECT 
D.name, 
D.kind, 
A.date, 
C.content  
FROM crises_crisis AS A INNER JOIN crises_listtype AS B ON A.wcdbelement_ptr_id == B.element 
INNER JOIN crises_li AS C on B.ID == C.ListID 
LEFT JOIN crises_wcdbelement AS D on B.element == D.ID 
WHERE A.date > "2001-12-31" AND B.content_type == "ECONOMICIMPACT" AND (D.kind LIKE "%Natural%" OR D.kind LIKE "%natural%") ;

SELECT "================================================================================================="
SELECT "SQL for queries from the other teams"
SELECT "================================================================================================="

SELECT "1.The number of images of all events prior to the year 2000"

SELECT 
SUM(num_elements) AS total_images 
FROM crises_listtype AS A LEFT JOIN crises_crisis AS B ON A.element == B.wcdbelement_ptr_id 
WHERE content_type == "IMAGES" AND B.date < "2000-01-01";

SELECT "2.organizations that have at least 2 related videos"

SELECT  
B.name, 
C.num_elements  
FROM crises_organization AS A INNER JOIN crises_wcdbelement AS B ON A.wcdbelement_ptr_id == B.ID 
INNER JOIN crises_listtype AS C on B.ID == C.element 
WHERE C.content_type == "VIDEOS" AND num_elements >= 2 ;

SELECT "3.people linked to at least 2 crises"

SELECT name, 
link  
FROM 
(
SELECT person, name,  COUNT(*) AS link 
FROM crises_r_crisis_person AS per LEFT JOIN crises_wcdbelement AS elem  ON per.person == elem.ID  
GROUP BY person
) AS A  
WHERE A.link >= 2;

SELECT "4.Crises that took place between 12 am and 12 pm"

SELECT 
A.name 
FROM crises_wcdbelement AS A INNER JOIN crises_crisis AS B ON A.ID == B.wcdbelement_ptr_id  
WHERE time BETWEEN "00:00:00" AND "12:00:00" ;

SELECT "5.Show the person/people with the most images."

SELECT name FROM
(
SELECT 
B.name AS name , 
SUM(CASE WHEN content_type == "IMAGES" THEN num_elements ELSE 0 END) AS image_cnt FROM crises_listtype AS A LEFT JOIN crises_wcdbelement AS B ON A.element == B.ID  WHERE B.ID LIKE "%PER_%" AND content_type == "IMAGES" GROUP BY element ORDER BY image_cnt DESC
) AS tab
WHERE image_cnt = (
SELECT MAX(image_cnt) 
FROM (
SELECT 
B.name AS name , 
SUM(CASE WHEN content_type == "IMAGES" THEN num_elements ELSE 0 END) AS image_cnt FROM crises_listtype AS A LEFT JOIN crises_wcdbelement AS B ON A.element == B.ID  WHERE B.ID LIKE "%PER_%" AND content_type == "IMAGES" GROUP BY element ORDER BY image_cnt DESC
)
);
