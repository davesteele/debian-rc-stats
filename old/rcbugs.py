#!/usr/bin/python3

import psycopg2.extensions
from collections import namedtuple, OrderedDict
from datetime import datetime
import pprint




bugparams = """
    id
    package
    source
    arrival
    status
    severity
    submitter
    submitter_name
    submitter_email
    owner
    owner_name
    owner_email
    done
    done_name
    done_email
    title
    last_modified
    forwarded
    affects_oldstable
    affects_stable
    affects_testing
    affects_unstable
    affects_experimental
    affected_packages
    affected_sources
    """.split()


extendedParams = """
    found_in
    fixed_in
    """.split()


maxLastModified = 0

allParams = bugparams + extendedParams

def getAllParams():
    return allParams


def getParamType(param):
    if param in ['last_modified', 'arrival']:
        return "integer"
    else:
        return "text"


def convertDate(strdate):
    try:
        return int(strdate.timestamp())
    except ValueError:
        return 0


def convertBool(val):
    if val:
        return "True"
    else:
        return "False"


def get_ver(conn, id, table):
    returnvalue = ""
    c = conn.cursor()
    c.execute("SELECT version FROM %s where id = %s" % (table, id))

    for version in c:
        returnvalue = version[0]
        if '/' in returnvalue:
            returnvalue = returnvalue.split('/')[-1]

    c.close()

    return returnvalue


def bugFixup(bugdist, conn):
    for field in 'arrival', 'last_modified':
        bugdist[field] = convertDate(bugdist[field])

    for field in "affects_stable", "affects_unstable",  "affects_oldstable", "affects_testing", "affects_experimental":
        bugdist[field] = convertBool(bugdist[field])

    bugdist["found_in"] = get_ver(conn, bugdist['id'], "archived_bugs_found_in")
    bugdist["fixed_in"] = get_ver(conn, bugdist['id'], "archived_bugs_fixed_in")


def rcbugs(old_max_last_modified = 0):
    global maxLastModified
    maxLastModified = old_max_last_modified

    conn = psycopg2.connect("dbname=udd user=udd-mirror password=udd-mirror host=udd-mirror.debian.net")
    conn.set_client_encoding("UTF8")

    cursor = conn.cursor()
    print 
    cursor.execute("SELECT %s FROM archived_bugs WHERE severity >= 'serious'::bugs_severity LIMIT 100" % ', '.join(bugparams))
    
    for bug in cursor:
        bugdist = dict(zip(bugparams, bug))
        bugFixup(bugdist, conn)
        maxLastModified = max(maxLastModified, int(bugdist["last_modified"]))
        print(maxLastModified, bugdist["last_modified"], int(bugdist["last_modified"]))

        if int(bugdist["last_modified"]) > old_max_last_modified:
            yield bugdist

    cursor.close()



if __name__ == '__main__':
    pp = pprint.PrettyPrinter()
    for bug in rcbugs():
        pp.pprint(bug)

    print(maxLastModified)

