#!/usr/bin/python3

import sys
import sqlite3
import testuploads

import datetime

import logging

# Class implementing persistent storage and query for testing package versions
# vs. date.

class TestMigrations(object):
    def __init__(self, connection):
        self.connection = connection

        try:
            c = self.connection.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS migrations (
                             date integer,
                             package text,
                             version text
                         )"""
            )

            c.execute("CREATE TABLE IF NOT EXISTS processed_urls (url text)")
            c.close()

            self.connection.commit()

        except sqlite3.OperationalError:
            pass

    def populate(self):

        def haveISeenIt(url, done=False):
            c = self.connection.cursor()
            retval = None

            if done == False:
                c.execute("SELECT * from processed_urls where url = \"%s\"" % url)
                retval = c.fetchone() != None
            else:
                c.execute("INSERT INTO processed_urls VALUES (\"%s\")" % url)
                self.connection.commit()

            c.close()
            return retval

        cur = self.connection.cursor()

        for m in testuploads.process_testing_updates(haveISeenIt):
            logging.debug("Adding migration - %s version %s" % (m[1], m[2]))

            cur.execute("INSERT into migrations VALUES (%d, \"%s\", \"%s\")" % (m[0].timestamp(), m[1], m[2]))
            self.connection.commit()

    def get_testing_version(self, package, date):
        version = None
        c = self.connection.cursor()

        c.execute("SELECT version from migrations where package = \"%s\" and date <= %d" % (package, date))

        try:
            version = c.fetchall()[-1][0]
        except IndexError:
            # Return None if no version found
            pass
        finally:
            c.close()

        return version

if __name__ == '__main__':
    """test code for this module"""

    log = logging.getLogger('uploadsdb')

    ch = logging.StreamHandler(sys.stdout)
    logging.basicConfig(level=logging.INFO, handlers=[ch])

    connection = sqlite3.connect('database.db')
    tm = TestMigrations(connection)

    tm.populate()

    print("The latest version of %s is %s" % ('gnome-gmail', tm.get_testing_version('gnome-gmail', datetime.datetime.now().timestamp())))
