#!/usr/bin/python3

from functools import wraps
import requests
import datetime
from lxml import html
from collections import namedtuple
import re
import logging

# process_testing_updates() is a generator that returns recent and
# unprocessed package migrations to testing, obtained via screen
# scrape of the debian-testing-changes mailing list.
#
# Each entry is represented as (<datetime object>, package, version).


log = logging.getLogger('testuploads')


archive_url = "https://lists.debian.org/debian-testing-changes/"
month_template="debian-testing-changes-"
day_template="msg"



def get_links(url, template, text_template="", baseurl=""):
    page = requests.get(url).text
    doc = html.fromstring(page)

    for link in doc.cssselect("a"):
        url = link.attrib['href']
        text = link.text_content()
        if template in url and text_template in text:
            yield baseurl + url

def reget(url):
    while True:
        try:
            return requests.get(url, timeout=10).text
        except requests.exceptions.ReadTimeout:
            print("retrying ", url)
            
def process_day(url, checkfn=None):
    print("  Processing day ", url)
    if not checkfn(url, done=False):
        page = reget(url)
        doc = html.fromstring(page)
    
        title = doc.cssselect("title")[0].text_content()
        datematch = re.search("Testing migration summary (.+) ", title)
        if not datematch:
            return
    
        datestring = datematch.group(1)
        try:
            dateobj = datetime.datetime.strptime(datestring, "%Y-%m-%d")
        except ValueError:
            return

        log.info("Processing summary " + dateobj.isoformat()[0:10])
    
        body = doc.cssselect("pre")[0].text_content()
        table = re.search("----$(.+)^--", body, re.MULTILINE | re.DOTALL).group(1)
        for line in table.split('\n'):
            print("    Processing line ", line)
            if line[0:2] == "  ":
                tags = line.split()
                yield [int(dateobj.timestamp())] + tags[0:2]

        checkfn(url, done=True)


def process_month(url, checkfn=None):
    print("Processing month ", url)
    if not checkfn(url, done=False):
        pagename = url.split('/')[-2]
        datestr = pagename.split('-')[-1]
        monthdt = datetime.datetime.strptime(datestr, "%Y%m")
        log.info("Processing month " + monthdt.isoformat()[0:7])

        baseurl = url[:-len("threads.html")]
        for link in get_links(url, day_template, text_template="summary", baseurl=baseurl):
            for entry in process_day(link, checkfn=checkfn):
                yield entry

        expiredate = monthdt.timestamp() + 60*60*24*40
        if expiredate < datetime.datetime.now().timestamp():
            checkfn(url, done=True)


def process_testing_updates(checkfn=None):
    for link in get_links(archive_url, month_template, baseurl=archive_url):
        for entry in process_month(link, checkfn):
            yield entry


if __name__ == '__main__':
    def haveISeenIt(x, done=False):
        return False
    callback = lambda x, y:False
    timestamps = []
    for entry in process_testing_updates(haveISeenIt):
        print(entry)
        timestamps.append(entry)

    json.dump(timestamps, open("uploads.json", 'w'), sort_keys=True, indent=2)



