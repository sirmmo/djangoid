from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse as urlreverse
from openid.server import server
from django.contrib.auth.models import User
from server.views import getDjangoidUserFromIdentity
from users.models import TrustedRoot, DjangoidUser, UserAttribute
from openidhandlers import convertToOpenIDRequest, checkYadisRequest, convertToHttpResponse
from microidutils import microid
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

def useryadis(request, uid):
        uid = User.objects.get(username = uid)
        res = render_to_response("users/yadis.xrds", {"server_url": settings.BASE_URL[:-1] + urlreverse("server.views.endpoint"), "uid": uid})
        mimetype = "application/xrds+xml; charset=%s" % settings.DEFAULT_CHARSET
        res["Content-Type"] = mimetype
        return res

def userpage_short(request, uid):
        uid = User.objects.get(username = uid)
        #Check whether this is a YADIS request
        if checkYadisRequest(request):
                return useryadis(request, uid.username)

        user = DjangoidUser.objects.get(djangouser = uid)
        user.attributes = user.get_attributes(True)
        mid = microid(user.get_user_page(), user.get_user_page())
        res = render_to_response("users/userpage.html", {"server_url": settings.BASE_URL[:-1] + urlreverse("server.views.endpoint"), "user": user, "microid": mid})
        res["X-XRDS-Location"] = user.get_yadis_uri()
        return res
@login_required
def userpage(request, uid):
        uid = User.objects.get(username = uid)
        user = DjangoidUser.objects.get(djangouser = uid)
        user.attributes = user.get_attributes(True)
        mid = microid(user.get_user_page(), user.get_user_page())
        res = render_to_response("users/userpage.html", {"server_url": settings.BASE_URL[:-1] + urlreverse("server.views.endpoint"), "user": user, "microid": mid})
        res["X-XRDS-Location"] = user.get_yadis_uri()
        return res


@csrf_exempt
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
	uid = User.objects.get(username = uid)
        user = DjangoidUser.objects.get(djangouser = uid)
        return HttpResponse(user.get_foaf().serialize(format = "pretty-xml"))
