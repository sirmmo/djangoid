from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()
urlpatterns = patterns('',
    url(r'^testid/$', 'users.views.testid'),
    url(r'^yadis/$', 'server.views.serveryadis'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', {"template_name": "users/login.html"}),
    url(r'^accept/$', 'users.views.accept'),
    url(r'^(?P<uid>[^/]+)/yadis/$', 'users.views.useryadis'),
    url(r'^(?P<uid>[^/]+)/foaf/$', 'users.views.userfoaf'),
    url(r'^(?P<uid>[^/]+)/$', 'users.views.userpage'),
    url(r'^$', 'server.views.endpoint'),
)
