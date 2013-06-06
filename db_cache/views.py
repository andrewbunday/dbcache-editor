import os
import re
import pwd
import stat
import time
from functools import wraps
from collections import defaultdict
import shutil

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

    print potential_show_folders

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
        #js_data = json.dumps(data)

        return render_template('editor.html', fields=data, showname=showname)

@app.route('/save/<showname>', methods=['POST'])
def save_cache(showname):
    """save callback"""

    # form_data = {}
    # for row in request.form:
    #     id_, key = re.findall('(\d+)\[([a-z]+)\]', row)[0]
    #     value = request.form.getlist(row)[0]
    #     if id_ not in form_data:
    #         form_data[id_] = {}
    #     form_data[id_][key] = value

    # @TODO backup original path_cache.db
    # shutil.copy('/mnt/shows/{0}/tank/cache/path_cache.db'.format(showname),
    #            '/mnt/shows/{0}/tank/cache/path_cache.db.1'.format(showname))

    with Connector('/mnt/shows/{0}/tank/cache/path_cache.db.1'.format(showname)) as db:
        # this way the connection is automatically destroyed then the page has
        # been loaded.

        # get some info about our table
        db.cur.execute("PRAGMA table_info(path_cache)")
        table_info = db.cur.fetchall()

        # old with the old
        db.cur.execute("DELETE FROM path_cache")
        db.con.commit()

        # in with the new
        for key in sorted(request.json.keys()):
            row_data = request.json[key]

            # munge the insert query to match the schema of the table
            if len(table_info) == 6:
                query = "INSERT INTO path_cache VALUES({id}, '{type}', '{name}', 'primary', '{path}', 1)".format(**row_data)
            else:
                query = "INSERT INTO path_cache VALUES({id}, '{type}', '{name}', 'primary', '{path}')".format(**row_data)

            try:
                db.cur.execute(query)
            except sqlite3.OperationalError:
                print "insert into database failed: ",
            finally:
                print query

            try:
                db.con.commit()
            except sqlite3.OperationalError:
                print "unable to commit changes to database"
                return

    return "success"
