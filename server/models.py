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
from django.db import models

#These are some dumb mappings of the original OpenID store tables as used by the SQLStore implemenation(s).
#They're used by "DjangoidStore"
class OidStoreNonce(models.Model):
        nonce = models.CharField(max_length = 8, primary_key = True)
        expires = models.IntegerField()

class OidStoreAssociation(models.Model):
        server_url = models.TextField()
        handle = models.CharField(max_length = 255)
        secret = models.TextField()
        issued = models.IntegerField()
        lifetime = models.IntegerField()
        assoc_type = models.CharField(max_length = 64)

        class Meta:
                #Django got no multi-column primary keys
                unique_together = (("server_url", "handle"),)

class OidStoreSetting(models.Model):
        setting = models.CharField(max_length = 128, primary_key = True)
        value = models.TextField()
