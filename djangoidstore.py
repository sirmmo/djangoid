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
import time, base64
from server.models import OidStoreNonce, OidStoreAssociation, OidStoreSetting
from openid.store.interface import OpenIDStore
from openid.association import Association
from openid import cryptutil

#This is a pretty dumb rewrite of the original SqlStore
class DjangoidStore(OpenIDStore):
        def __init__(self):
                self.max_nonce_age = 6 * 60 * 60 # Six hours, in seconds

        #Use base64 in a TextField, as this can be non-text data, and django got no BlobField.
        #Storing binary data in a TextField makes django choke because the "text" can't be converted to eg UTF8
        def blobDecode(self, blob):
                return base64.decodestring(blob)

        def blobEncode(self, s):
                return base64.encodestring(s)

        def storeAssociation(self, server_url, association):
                OidStoreAssociation.objects.filter(server_url = server_url, handle = association.handle).delete()
                a = OidStoreAssociation(server_url = server_url, handle = association.handle, secret = self.blobEncode(association.secret), issued = association.issued, lifetime = association.lifetime, assoc_type = association.assoc_type)
                a.save()

        def getAssociation(self, server_url, handle = None):
                associations = None
                if handle is not None:
                        associations = OidStoreAssociation.objects.filter(server_url = server_url, handle = handle)
                else:
                        associations = OidStoreAssociation.objects.filter(server_url = server_url)
                if associations.count() == 0:
                        return None
                else:
                        assocs = []
                        for a in associations:
                                adata = [a.handle, self.blobDecode(a.secret), a.issued, a.lifetime, a.assoc_type]

                                assoc = Association(*adata)

                                if assoc.getExpiresIn() == 0:
                                        self.removeAssociation(server_url, assoc.handle)
                                else:
                                        assocs.append((assoc.issued, assoc))
                         
                        if assocs:
                                assocs.sort()
                                return assocs[-1][1]
                        else:
                                return None

        def removeAssociation(self, server_url, handle):
                assocs = OidStoreAssociation.objects.filter(server_url = server_url, handle = handle)
                cnt = assocs.count()
                assocs.delete()
                return cnt > 0

        def storeNonce(self, nonce):
                now = int(time.time())
                nonce = OidStoreNonce(nonce = nonce, expires = now)
                nonce.save()

        def useNonce(self, nonce):
                nonce = OidStoreNonce.objects.get(nonce = nonce)
                if nonce.count() <= 0:
                        present = 0
                else:
                        nonce_age = int(time.time()) - nonce.timestamp
                        if nonce_age > self.max_nonce_age:
                                present = 0
                        else:
                                present = 1

                        nonce.delete()

                return present

        def getAuthKey(self):
                key = OidStoreSetting.objects.get(setting = "auth_key")
                if key.count() == 0:
                        auth_key = cryptutil.randomString(self.AUTH_KEY_LEN)
                        s = OidStoreSetting(setting = "auth_key", value = self.blobEncode(auth_key))
                        s.save()
                else:
                        auth_key = self.blobDecode(key.value)

                if len(auth_key) != self.AUTH_KEY_LEN:
                        fmt = "Expected %d-byte string for auth key, got %r"
                        raise ValueError(fmt % (self.AUTH_KEY_LEN, auth_key))

                return auth_key

        def isDumb(self):
                return False
