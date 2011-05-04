from django.http import HttpResponse, HttpResponseRedirect
import settings
from django.shortcuts import render_to_response
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse as urlreverse
from django.contrib.auth.models import User as DjangoUser
from users.models import DjangoidUser, ClaimedUri
from openidhandlers import checkYadisRequest, convertToOpenIDRequest, convertToHttpResponse, handleOpenIDRequest 
import re
import urllib

from django.views.decorators.csrf import csrf_exempt
#Get a DjangoidUser object, based on a delegate URI
def getDjangoidUserFromIdentity(identity):
        s = settings.BASE_URL[:-1] + (urlreverse("user_entrypoint", kwargs = {"uid": "@blah@"})[:-1].replace("@blah@", "(?P<uid>[^/]+)/"))
        print s
        _identityRe = re.compile(s)
        uid = _identityRe.match(identity).groupdict()["uid"]
        user = DjangoidUser.objects.filter(djangouser__username = uid)
        if not len(user) == 0:
                return user[0]
        else:
                if DjangoUser.objects.filter(username = uid).count() == 0:
                        raise Exception, ("This user does not exist: " + uid)
                user = DjangoidUser(djangouser = uid)
                user.save()
                c = ClaimedUri(user = user, uri = user.get_user_page())
                c.save()
                return user
@csrf_exempt
def endpoint(request):
        #If this is (most likely) a YADIS request, handle it using the YADIS view function
        if checkYadisRequest(request):
                return serveryadis(request)

        r = convertToOpenIDRequest(request)

        #If the request wasnt a valid OpenID server request, render some static page.
        #TODO: use render_to_response("about.html")
        if r is None:
                return HttpResponse("about")

        #Check whether we got to do anything...
        if r.mode in ["checkid_immediate", "checkid_setup"]:
                #Get a DjangoidUser, based on the identity URI
                user = getDjangoidUserFromIdentity(r.identity)
                #If the user is not in our database yet, or he's not authenticated (or authenticated using some other
                #username), redirect to the login page. This is part of the "users" application.
                #Make sure we pass all OpenID related information in the URL
                if not request.user or request.user.is_authenticated() == False:
                        return redirect_to_login(r.encodeToURL("/".join([""] + settings.BASE_URL.split("/")[3:])) + "&tr=" + urllib.quote(r.trust_root), login_url = settings.BASE_URL + "login/")
                if not request.user == user.djangouser:
                        raise Exception, "Logged in as " + request.user.username + " while expecting " + user.djangouser

                #Is the user authenticated, and does he trust this trust_root?
                if user.authenticate(r.trust_root): #user logged in (using r.identity and r.trust_root)
                        response = r.answer(True)
                #User is logged in, but hasnt added this trust_root to his list of permanently trusted roots.
                #If this is an immediate request, we can't ask the user now though. Reply with a failure, passing the
                #URI to which a second request (non-immediate) should be made. This is this same view.
                elif r.immediate:
                        response = r.answer(False, settings.BASE_URL)
                #Right, we got to ask the user whether he trusts this trust_root, and whether he wants to add it to his
                #list of permanently trusted roots. This is handled in the "users" application.
                else:
                        r.claimed_id = request.user.username
                        return HttpResponseRedirect(r.encodeToURL(settings.BASE_URL + "accept/"))
        #If not, let the OpenID server do everything for us :-)
        else:
                response = handleOpenIDRequest(r)

        return convertToHttpResponse(response)

#A server YADIS document is requested. I don't think this is widely used yet, but well... Let's just return it.
def serveryadis(request):
        res = render_to_response("server/yadis.xrds", {"server_url": settings.BASE_URL[:-1] + urlreverse("server.views.endpoint")})
        res["Content-Type"] = "application/xrds+xml; charset=%s" % settings.DEFAULT_CHARSET
        return res
