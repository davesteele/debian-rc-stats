#!/usr/bin/python


import rfc822
import StringIO
import json


pkgtxt = open("Packages", 'r').read()

srcfor = {}

for chunk in pkgtxt.split("\n\n"):
    fp = StringIO.StringIO(chunk)
    hdrs = rfc822.Message(fp)
    pkg = hdrs.getheader("Package")
    src = hdrs.getheader("Source", pkg)
    if pkg:
        print(pkg, src)
        srcfor[pkg] = src.split()[0]
    fp.close()

json.dump(srcfor, open("srclookup.json", 'w'), sort_keys=True, indent=2)
