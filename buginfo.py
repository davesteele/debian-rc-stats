#!/usr/bin/python

import json


bugs = json.load(open('bugs.json', 'r'))
comments = json.load(open('comments.json', 'r'))
srclookup = json.load(open('srclookup.json', 'r'))
uploads = json.load(open('uploads.json', 'r'))

outbugs = []


def version_on_date(srcpackage, tstamp):
    puploads = [x for x in uploads if x[1] == srcpackage]

    def rdfn(x, y):
        if y[0] < tstamp:
            return y
        else:
            return x

    current_release = reduce(rdfn, puploads)

    if current_release[0] < tstamp:
        return current_release[2]
    else:
        return None


for bug in bugs:

    if bug['package'][0:4] == "src:":
        bug['package'] = bug['package'][4:]

    bug_comments = [x for x in comments if x['id'] == bug['id']]
    bug['num_comments'] = len(bug_comments)

    if bug['done']:
        bug['closed'] = max([x['date'] for x in bug_comments])


    pkg = bug['package']
    ver = bug['version']
    srcpkg = pkg
    try:
        srcpkg = srclookup[pkg]
    except KeyError:
        pass

    try:
        release_date = [x[0] for x in uploads if x[1] == srcpkg and x[2] == ver][0]
    except IndexError:
        print "no match for ", pkg, srcpkg, ver
        continue

    print "VINFO - ", srcpkg, ver, bug['date'], version_on_date(srcpkg, bug['date'])

    if version_on_date(srcpkg, bug['date']) != ver:
        print "not in testing on bug creation date", pkg, srcpkg, ver
        continue



    bug['releasedate'] = release_date

    outbugs.append(bug)


    print bug


json.dump(outbugs, open('outbugs.json', 'w'), sort_keys=True, indent=2)
