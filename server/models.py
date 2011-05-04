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
