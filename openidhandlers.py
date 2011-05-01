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
from openid.server import server
from djangoid.djangoidstore import DjangoidStore
from django.http import HttpResponse

#OpenID server instance, using a DjangoidStore object as container
_openidserver = server.Server(DjangoidStore())

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
