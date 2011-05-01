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
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse as urlreverse
import datetime
from djangoid.microidutils import microid, find_microid

#Represent one trusted root URI. Can be shared between several users.
class TrustedRoot(models.Model):
        root = models.URLField("Trusted root URI", primary_key = True)

        def __str__(self):
                return self.root

        class Admin:
                pass

#Represent one system user, based on Django's internal user system.
class DjangoidUser(models.Model):
        #This seems not to work:
        #djangouser = models.ForeignKey(User, primary_key = True)
        #So using an ugly hack... TODO: Fixme!
        djangouser = models.CharField('Django user username', maxlength = 30, primary_key = True, help_text = "This should be the username of an existing user in the django.contrib.auth system")
        trusted_roots = models.ManyToManyField(TrustedRoot, blank = True, null = True, help_text = "URI's trusted by this user")

        def __str__(self):
                return self.djangouser

        def authenticate(self, root):
                r = TrustedRoot.objects.filter(root = root)
                if len(r) == 0: #Certainly not trusted
                        TrustedRoot(root = root).save()
                else:
                        for mr in self.trusted_roots.all():
                                if root == mr.root:
                                        return True
                return False

        def get_djangouser(self):
                return User.objects.get(username = self.djangouser)

        def get_user_page(self):
                #Strip of last / from BASE_URL
                return settings.BASE_URL[:-1] + urlreverse("djangoid.users.views.userpage", kwargs = {"uid": self.djangouser})

        def get_yadis_uri(self):
                return settings.BASE_URL[:-1] + urlreverse("djangoid.users.views.useryadis", kwargs = {"uid": self.djangouser})

        def get_name(self):
                """
                Get a (public) representation of the full name of a user

                >>> user = DjangoidUser(djangouser = "test")
                >>> user.get_name()
                'test'
                """
                f = None
                l = None
                try:
                        f = UserAttribute.objects.get(user = self, attribute__name__exact = "FIRST_NAME", public = True).value
                except:
                        pass
                try:
                        l = UserAttribute.objects.get(user = self, attribute__name__exact = "LAST_NAME", public = True).value
                except:
                        pass

                if l is None and f is None:
                        return self.djangouser
                else:
                        if l is None:
                                return f
                        if f is None:
                                return l
                        return f + " " + l

        def get_attributes(self, public = False):
                attributes = {}
                for a in UserAttribute.objects.filter(user = self, public = public):
                        attributes[a.attribute.name] = a.value
                return attributes

        def get_foaf(self):
                import sha
                try:
                        from rdflib.Graph import Graph
                        from rdflib import URIRef, Literal, BNode, Namespace, URIRef
                        from rdflib import RDF
                except ImportError:
                        raise Exception, "Please install RDFLib from http://rdflib.net"

                FOAF_NS = "http://xmlns.com/foaf/0.1/"

                store = Graph()
                store.bind("foaf", FOAF_NS)
                FOAF = Namespace(FOAF_NS)

                user = BNode()
                attributes = self.get_attributes(True)

                store.add((user, RDF.type, FOAF["Person"]))
                store.add((user, FOAF["name"], Literal(attributes["FIRST_NAME"] + " " + attributes["LAST_NAME"])))
                store.add((user, FOAF["family_name"], Literal(attributes["LAST_NAME"])))
                store.add((user, FOAF["nick"], Literal(attributes["NICKNAME"])))
                store.add((user, FOAF["homepage"], URIRef(attributes["HOMEPAGE_URI"])))
                store.add((user, FOAF["mbox_sha1sum"], Literal(sha.new(attributes["EMAIL"]).hexdigest())))
                store.add((user, FOAF["jabberID"], Literal(attributes["IM_JID"])))


                return store

        
        class Admin:
                pass

#Identities can have attributes. These items represent one possible attribute.
class IdentityAttribute(models.Model):
        name = models.CharField("Name", maxlength = 128, help_text = "Internal name of the attribute.", primary_key = True)
        title = models.CharField("Title", maxlength = 128, help_text = "Title of the attribute, as displayed to the user")
        description = models.TextField("Description", blank = True, help_text = "Longer description of the attribute, as displayed to the user")
        regex = models.CharField("Validation regex", maxlength = 128, blank = True, help_text = "Regex the value of this field is validated upon on updates")

        def __str__(self):
                return self.title

        class Admin:
                pass

#This maps an attribute to a user, including a value, obviously
class UserAttribute(models.Model):
        user = models.ForeignKey(DjangoidUser, help_text = "DjangoidUser this attribute value belongs to")
        attribute = models.ForeignKey(IdentityAttribute, help_text = "Attribute of which this is the value for this user")
        value = models.TextField("Value")
        #True if this attribute's value may be displayed to all trust roots
        public = models.BooleanField("Public", help_text = "If this is true, this attribute is returned in all authentication requests, of all trust roots")
        #List of specific trust roots this attribute may be displayed to.
        #If "public" is True, this got no meaning at all
        public_for = models.ManyToManyField(TrustedRoot, blank = True, null = True, help_text = "List of all trust roots this value should be displayed to. If \"public\" is true, this list got no value")

        def __str__(self):
                return str(self.user) + ": " + str(self.attribute)

        class Admin:
                pass

        class Meta:
                #Only store an attribute once for every user
                unique_together = (("user", "attribute"),)

#A claimed webpage. This will be checked using MicroID
class ClaimedUri(models.Model):
        user = models.ForeignKey(DjangoidUser)
        uri = models.URLField()
        description = models.CharField(maxlength = 128, blank = True)
        last_checked = models.DateTimeField(default = datetime.datetime(2006, 1, 1))
        is_valid = models.BooleanField(default = False)

        def __str__(self):
                return self.uri

        def get_contact_uri(self):
                return self.user.get_user_page()

        def get_microids(self):
                return [microid(self.get_contact_uri(), self.uri), microid("mailto:" + self.user.get_djangouser().email, self.uri)]

        def update_validity(self):
                found = find_microid(self.uri)
                self.last_checked = datetime.datetime.now()
                self.is_valid = False
                for id in self.get_microids():
                        if id in found:
                                self.is_valid = True
                self.save()

        class Admin:
                date_hierarchy = "last_checked"
                list_display = ("user", "uri", "is_valid", "get_microids",)
                list_filter = ("user", "is_valid",)
                search_fields = ["user", "uri"]

        class Meta:
                unique_together = (("user", "uri"),)
                get_latest_by = "last_checked"
                ordering = ["user", "is_valid", "last_checked"]
