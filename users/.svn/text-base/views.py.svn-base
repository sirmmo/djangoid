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
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse as urlreverse
from openid.server import server

from djangoid.server.views import getDjangoidUserFromIdentity
from djangoid.users.models import TrustedRoot, DjangoidUser, UserAttribute
from djangoid.openidhandlers import convertToOpenIDRequest, checkYadisRequest, convertToHttpResponse
from djangoid.microidutils import microid

def useryadis(request, uid):
        res = render_to_response("users/yadis.xrds", {"server_url": settings.BASE_URL[:-1] + urlreverse("djangoid.server.views.endpoint"), "uid": uid})
        mimetype = "application/xrds+xml; charset=%s" % settings.DEFAULT_CHARSET
        res["Content-Type"] = mimetype
        return res

def userpage(request, uid):
        #Check whether this is a YADIS request
        if checkYadisRequest(request):
                return useryadis(request, uid)

        user = DjangoidUser.objects.get(djangouser = uid)
        user.attributes = user.get_attributes(True)
        mid = microid(user.get_user_page(), user.get_user_page())
        res = render_to_response("users/userpage.html", {"server_url": settings.BASE_URL[:-1] + urlreverse("djangoid.server.views.endpoint"), "user": user, "microid": mid})
        res["X-XRDS-Location"] = user.get_yadis_uri()
        return res

def testid(request):
        return userpage(request, "nicolas")

def accept(request):
        r = convertToOpenIDRequest(request)

        if r is None:
                return HttpResponse("Nothing here")

        if request.method == "GET":
                return render_to_response("users/accept_root.html", {"openid_request": r})

        if request.method == "POST":
                if request.POST.has_key("cancel"):
                        return convertToHttpResponse(r.answer(False))
                if request.POST.has_key("remember"):
                        user = getDjangoidUserFromIdentity(r.identity)
                        root = TrustedRoot.objects.get(root = r.trust_root)
                        user.trusted_roots.add(root)
                return convertToHttpResponse(r.answer(True))

def userfoaf(request, uid):
        user = DjangoidUser.objects.get(djangouser = uid)
        return HttpResponse(user.get_foaf().serialize(format = "pretty-xml"))
