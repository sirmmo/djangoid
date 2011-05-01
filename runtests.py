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
import doctest, sys, os
sys.path.append("../")
os.environ["DJANGO_SETTINGS_MODULE"] = "djangoid.settings"

import microidutils
import openidhandlers
import users.models

mods = (
                microidutils,
                openidhandlers,
                users.models
       )

def run_tests():
        verbose = "-v" in sys.argv
        for mod in mods:
                print "=== Testing %s ===" % mod.__name__
                (fails, tests) = doctest.testmod(mod, verbose = verbose, report = 0)
                print ">>> %d tests run, %d failed" % (tests, fails)
                print
        print
        print "=== Summary ==="
        doctest.master.summarize(verbose)

if __name__ == "__main__":
        run_tests()
