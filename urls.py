from django.conf.urls.defaults import *

from django.contrib import admin
import views
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/(.*)', admin.site.root),
    (r'^$', views.home),
    (r'^(?P<slug>[A-Za-z0-9-]*)/$', views.redirect),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT})
    )