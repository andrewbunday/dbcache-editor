#!/usr/bin/env python

import sys
import sqlite3
import logging
import simplejson as json

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

#showname = raw_input("Please type the name of the show (on-disk) you want to edit: ")
#db_path = "/mnt/shows/%s/tank/cache/path_cache.db" % showname

#logging.debug("reading cachefile: %s" % db_path)

class Connector(object):
    def __init__(self, db_path):
        self.db_path = db_path

    def __enter__(self):
        logging.debug("__enter__ method entered")
        try:
            # check the connection work before handing back control
            self.con = sqlite3.connect(self.db_path)
            self.cur = self.con.cursor()
            self.cur.execute('SELECT SQLITE_VERSION()')
            if not self.cur.fetchone():
                raise sqlite3.Error()

        except sqlite3.Error as e:
            logging.debug('Unable to connect to db %s' % self.db_path)
            logging.debug(e.args[0])

        except Exception as e:
            raise

        return self

    def __exit__(self, type, value, tb):
        logging.debug("__exit__ method entered")
        if self.con:
            self.con.close()

if __name__ == "__main__":

    with Connector(db_path) as db:

        print db.con
        db.cur.execute('SELECT * FROM path_cache')
        data = db.cur.fetchall()
        print json.dumps(data)

 
