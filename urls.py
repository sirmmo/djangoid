#Djangoid - Django-based OpenID server/provider
#Copyright (C) 2006  Nicolas Trangez <ikke nicolast be>
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#EOL
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^djangoid/', include('djangoid.apps.foo.urls.foo')),
    (r'^testid/$', 'djangoid.users.views.testid'),
    (r'^yadis/$', 'djangoid.server.views.serveryadis'),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^login/$', 'django.contrib.auth.views.login', {"template_name": "users/login.html"}),
    (r'^accept/$', 'djangoid.users.views.accept'),
    (r'^(?P<uid>[^/]+)/yadis/$', 'djangoid.users.views.useryadis'),
    (r'^(?P<uid>[^/]+)/foaf/$', 'djangoid.users.views.userfoaf'),
    (r'^(?P<uid>[^/]+)/$', 'djangoid.users.views.userpage'),
    (r'^$', 'djangoid.server.views.endpoint'),
)
