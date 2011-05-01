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
#!/usr/bin/env python
import sys
import os

if os.environ["PWD"][-4:] == "/bin":
        sys.path.append("../..")
else:
        sys.path.append("../")
os.environ["DJANGO_SETTINGS_MODULE"] = "djangoid.settings"

from djangoid.users.models import ClaimedUri

def main():
        uris = ClaimedUri.objects.all()
        for uri in uris:
                uri.update_validity()

                print "Checked", uri.uri, "for", uri.user.djangouser,", result is", uri.is_valid


if __name__ == "__main__":
        main()
