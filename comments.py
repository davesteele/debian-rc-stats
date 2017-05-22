#!/usr/bin/python

import os
import re
import rfc822
import StringIO
import calendar
import json

""" Get statistics on messages associated with a Debian bug
    This requires that the data downloaded by getbts is present,
    and that this is run in the same directory as getbts.


    Main Interface
    process_comments()
        args
            bug - the bug number, as text
    
        returns
            a list of dicts, one for each message related to the bug:
                - date - unix time
                - from - the from header entry
                - name - the 'From' name (or "")
                - email - the 'From' email address

    main() creates a bugs.json and comments.json file with details of
    release critical bugs created during the Jessie era.
"""
    

SPOOLDIR="btsspool"
SPOOLS=["bts-spool-archive", "bts-spool-db"]

def get_bug_path(bug):

    cachedir = bug[-2:]
    for spool in SPOOLS:
        candidate = os.path.join(SPOOLDIR, spool, cachedir, bug)
        if os.path.exists(candidate + ".log"):
            return candidate

    return None


def get_bug_text(bug):
    return open(get_bug_path(bug) + ".log", 'r').read()


def get_bug_headers(bugtext):
    messages = re.split("\x07\x0a", bugtext)[1:]
    headers = [x.split("\n\n")[0] for x in messages]
    return headers


def parse_bug_header(header):
    fp = StringIO.StringIO(header)
    message = rfc822.Message(fp)

    msgdict = {}

    msgdict['from'] = message.getheader('From')
    name, email = message.getaddr('From')
    msgdict['name'] = name if name else ""
    msgdict['email'] = email if email else ""

    try:
        msgdict['date']  = calendar.timegm(message.getdate('Date'))
    except:
        msgdict['date'] = 0
    
    return msgdict


def get_comments(bugtext):
    headers = {}

    for header in get_bug_headers(bugtext):
        entry = parse_bug_header(header)

        headers[entry['date']] = entry

    return sorted([headers[x] for x in headers], key = lambda x: x['date'])


def process_comments(bug):
    return get_comments(get_bug_text(bug))


def bug_iter():
    for spool in SPOOLS:
        for cachedir in ["%.2d" % x for x in range(0,100)]:
            dir = os.path.join("btsspool", spool, cachedir)
            logbugs = [x[:-4] for x in os.listdir(dir) if x[-4:] == ".log"]
            sumbugs = [x[:-8] for x in os.listdir(dir) if x[-8:] == ".summary"]

            for bug in set(logbugs) & set(sumbugs):
                yield bug


def get_bug(bugnum):
    fp = open(get_bug_path(bugnum) + ".summary", 'r')
    message = rfc822.Message(fp)

    bug = {}

    bug['done'] = False
    if message.getheader("Done", ""):
        bug['done'] = True
    bug['date'] = int(message.getheader("Date", "0"))

    bug['version'] = message.getheader("Found-In", "")
    if " " in bug['version']:
        bug['version'] = bug['version'].split()[0]
    if "/" in bug['version']:
        bug['version'] = bug['version'].split('/')[1]

    bug['package'] = message.getheader("Package", "")

    bug['id'] = int(bugnum)

    bug['severity'] = message.getheader("Severity", "normal")

    fp.close()

    return bug


def get_bugs_filtered(filterfn):
    for bugnum in bug_iter():
        bug = get_bug(bugnum)
        if filterfn(bug):
            yield bug

    
if __name__ == "__main__":

    def filter(bug):
        if bug['date'] < 1414800000:
            return False

        if not bug['version']:
            return False

        if not bug['package']:
            return False

        if bug['severity'] not in ['serious', 'grave', 'critical']:
            return False

        return True

    bugs = []
    comments = []

    for bug in get_bugs_filtered(filter):

        print bug
        bugs.append(bug)

        for comment in process_comments(str(bug['id'])):
            comment['id'] = bug['id']
            print "    ", comment
            comments.append(comment)

    with open("bugs.json", 'w') as bugfp:
        json.dump(bugs, bugfp, sort_keys=True, indent=2)

    with open("comments.json", 'w') as commentfp:
        json.dump(comments, commentfp, sort_keys=True, indent=2)
