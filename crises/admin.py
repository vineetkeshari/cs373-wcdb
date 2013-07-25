from django.contrib import admin
from crises.models import Crisis, Organization, Person, ListType, LI, R_Crisis_Org, R_Crisis_Person, R_Org_Person

admin.site.register(Crisis)
admin.site.register(Organization)
admin.site.register(Person)
admin.site.register(ListType)
admin.site.register(LI)
admin.site.register(R_Crisis_Org)
admin.site.register(R_Crisis_Person)
admin.site.register(R_Org_Person)

