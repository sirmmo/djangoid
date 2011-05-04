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
