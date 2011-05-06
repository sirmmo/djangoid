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
