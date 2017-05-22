#!/usr/bin/python3

import sqlite3
import rcbugs



class BugsDB(object):
    def __init__(self, connection):
        self.connection = connection

        rc_fields = [(x, rcbugs.getParamType(x)) for x in rcbugs.bugparams]
        fields = rc_fields + [
                ('processed', 'text')
            ]

        fieldspec = ', '.join(["%s %s" % (x[0], x[1]) for x in fields])
        c = self.connection.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS bugs (%s)" % fieldspec)
        c.execute("CREATE TABLE IF NOT EXISTS max_last_mod (date integer)")

        self.connection.commit()

        c.close()


    def getMaxLastMod(self):
        returnValue = 0

        c = self.connection.cursor()

        c.execute("SELECT date from max_last_mod")

        for x in [x[0] for x in c]:
            returnValue = x
        c.close()

        return returnValue


    def setMaxLastmod(self, val):

        c = self.connection.cursor()
        c.execute("DELETE FROM max_last_mod")
        c.execute("INSERT INTO max_last_mod VALUES (%d)" % val)
        c.close()
        self.connection.commit()




if __name__ == '__main__':
    connection = sqlite3.connect('database.db')

    bugsdb = BugsDB(connection)

    
