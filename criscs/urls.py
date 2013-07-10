from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'crises.views.index'),
    url(r'^crises/$', 'crises.views.index'),
    url(r'^crises/(?P<view_id>\w{10})/$', 'crises.views.base_view'),
    # url(r'^criscs/', include('criscs.foo.urls')),

    url(r'^import/$', 'crises.views.import_file', name='import_file'),
    url(r'^export/$', 'crises.views.export_file', name='export_file'),
    url(r'^unittests/$', 'crises.views.run_tests', name='run_tests'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
