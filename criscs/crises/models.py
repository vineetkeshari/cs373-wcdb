from django.db import models

# Create your models here.

class XMLFile (models.Model) :
    """
    Store the latest XML file uploaded.
    """
    timestamp = models.DateTimeField (auto_now_add=True)
    xml_file = models.FileField (upload_to='xml/%Y%m%d')

class WCDBElement (models.Model) :
    """
    Base class for crisis, person and organization
    Contains primary key
    """
    ID = models.CharField (max_length=10, primary_key=True)
    name = models.CharField (max_length=200)
    kind = models.CharField (max_length=200, null=True)
    summary = models.TextField (max_length=2000, null=True)

class Crisis (WCDBElement) :
    """
    Crisis type extends WCDBElement
    """
    date = models.DateField (null=True)
    time = models.TimeField (null=True)

class Person (WCDBElement) :
    """
    Person type extends WCDBElement
    """
    location = models.CharField (max_length=200, null=True)

class Organization (WCDBElement) :
    """
    Organization type extends WCDBElement
    """
    location = models.CharField (max_length=200, null=True)

class Text_Store (models.Model) :
    """
    Stored text
    """
    ID = models.CharField (max_length=10, primary_key=True)
    content = models.TextField (max_length=1000000)

class R_Crisis_Person (models.Model) :
    """
    Stores relations between Crises and People
    """
    crisis = models.CharField (max_length=10)
    person = models.CharField (max_length=10)

class R_Crisis_Org (models.Model) :
    """
    Stores relations between Crises and Organizations
    """
    crisis = models.CharField (max_length=10)
    org = models.CharField (max_length=10)

class R_Org_Person (models.Model) :
    """
    Stores relations between Organizations and People
    """
    org = models.CharField (max_length=10)
    person = models.CharField (max_length=10)

class ListType (models.Model) :
    """
    ListType is based on the ListType in the XSD schema.
    List elements are stored in LI model and reference the ID field.
    element : The WCDBElement (Crisis, Person or Org) this List belongs to.
    content_type : The kind of content the list contains (images, history, etc).
    ID : Concatenation of element and content_type to give a unique identifier.
    """
    ID = models.CharField (max_length=200, primary_key=True)
    element = models.CharField (max_length=10)
    content_type = models.CharField (max_length=50)
    num_elements = models.IntegerField ()

class LI (models.Model) :
    """
    LI model is a list entry in ListType.
    ListID : The list this list entry belongs to.
    order : If order is important, this field stores the position in the list.
    content, href, embed, text : These contain the content in the list entry as defined in the XSD.
    """
    ListID = models.CharField (max_length=30)
    order = models.IntegerField ()
    content = models.TextField (max_length=1000, null=True)
    href = models.TextField (max_length=1000, null=True)
    embed = models.TextField (max_length=1000, null=True)
    text = models.TextField (max_length=1000, null=True)
    
