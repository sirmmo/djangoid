from openid.server import server
from djangoidstore import DjangoidStore
from django.http import HttpResponse
import settings
#OpenID server instance, using a DjangoidStore object as container
_openidserver = server.Server(DjangoidStore(), settings.BASE_URL)

def convertToHttpResponse(response):
        #Convert an OpenID server response to a Django-compatible HttpResponse:
        #copy HTTP headers, and payload
        r = _openidserver.encodeResponse(response)
        ret = HttpResponse(r.body)
        for header, value in r.headers.iteritems():
                ret[header] = value
        ret.status_code = r.code

        return ret

def convertToOpenIDRequest(request):
        #Copy over all query (GET and POST) key-value pairs, so we can pass them to out OpenID server.
        #request.REQUEST.copy() seems not to work, as openidserver.decodeRequest seems to use some function
        #on the passed object that's not implemented in the copied object.
        query = {}
        for i in request.REQUEST.items():
                query[i[0]] = i[1]
        try:
                return _openidserver.decodeRequest(query)
        except server.ProtocolError, why:
                raise

def checkYadisRequest(request):
        """
        Checks whether an incoming django.http.HttpRequest is a YADIS request

        >>> class Request:
        ...     def __init__(self, meta = {}):
        ...             self.META = meta
        ...
        >>> request = Request()
        >>> checkYadisRequest(request)
        False
        >>> request = Request({"HTTP_ACCEPT": "text/html"})
        >>> checkYadisRequest(request)
        False
        >>> request = Request({"HTTP_ACCEPT": "application/xrds+xml"})
        >>> checkYadisRequest(request)
        True
        """
        if request.META.has_key("HTTP_ACCEPT"):
                ct = request.META["HTTP_ACCEPT"]
                if "application/xrds+xml" in ct:
                        return True
        return False

def handleOpenIDRequest(request):
        return _openidserver.handleRequest(request)
