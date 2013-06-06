import os
import re
import pwd
import stat
import time
from functools import wraps
from collections import defaultdict
import shutil
import glob

# Application framework imports
from flask import render_template
from flask import send_file
from flask import redirect
from flask import url_for
from flask import request
from flask import Response
from flask import json
from flask import g

# Application setup/configuration etc.
from . import app
from db_connector import Connector, sqlite3

@app.route('/')
def index():
    """simple display of available caches"""

    potential_show_folders = os.listdir('/mnt/shows')
    actual_show_folders = []

    for f_ in potential_show_folders:
        if os.path.exists('/mnt/shows/{0}/tank/cache/path_cache.db'.format(f_)):
            print "%s cache db found" % f_
            actual_show_folders.append(f_)

    return render_template('index.html', shows=sorted(actual_show_folders))

@app.route('/editor/<showname>')
def editor(showname):
    """db_editor page"""

    with Connector('/mnt/shows/{0}/tank/cache/path_cache.db'.format(showname)) as db:
        # this way the connection is automatically destroyed then the page has
        # been loaded.
        db.cur.execute('SELECT * FROM path_cache ORDER BY entity_type, entity_name')
        data = db.cur.fetchall()

        return render_template('editor.html', fields=data, showname=showname)

@app.route('/save/<showname>', methods=['POST'])
def save_cache(showname):
    """save callback"""

    cache_files = glob.glob('/mnt/shows/{0}/tank/cache/path_cache*'.format(showname))
    cache_files.sort()

    if len(cache_files[-1].split('.')) > 2:
        # increment last
        prefix, suffix, incr = cache_files[-1].split('.')
        incr = int(incr) + 1
        backup_cache = ".".join([prefix, suffix, str(incr)])
    else:
        backup_cache = '/mnt/shows/{0}/tank/cache/path_cache.db.1'.format(showname)

    shutil.copy('/mnt/shows/{0}/tank/cache/path_cache.db'.format(showname), backup_cache)
    os.chown(backup_cache, 1900, 20)

    with Connector('/mnt/shows/{0}/tank/cache/path_cache.db'.format(showname)) as db:
        # this way the connection is automatically destroyed then the page has
        # been loaded.

        # get some info about our table
        db.cur.execute("PRAGMA table_info(path_cache)")
        table_info = db.cur.fetchall()
        print table_info

        # old with the old
        db.cur.execute("DELETE FROM path_cache")
        db.con.commit()

        # in with the new
        for key in sorted(request.json.keys()):
            row_data = request.json[key]

            # munge the insert query to match the schema of the table
            if len(table_info) == 6:
                query = "INSERT INTO path_cache VALUES('{type}', {id}, '{name}', 'primary', '{path}', 1)".format(**row_data)
            else:
                query = "INSERT INTO path_cache VALUES('{type}', {id}, '{name}', 'primary', '{path}')".format(**row_data)

            try:
                db.cur.execute(query)
            except sqlite3.OperationalError as e:
                print e
                print "insert into database failed: ",
            finally:
                print query

            try:
                db.con.commit()
            except sqlite3.OperationalError:
                print "unable to commit changes to database"
                return "fail"

    return "success"
