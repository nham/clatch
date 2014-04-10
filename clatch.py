from models import Tag, Log, Page

import os
import sqlite3
import time
from slugify import slugify # awesome-slugify

from flask import Flask, request, g, jsonify, abort, make_response

from subprocess import Popen, PIPE

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'clatch.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='funky'
))
app.config.from_envvar('CLATCH_SETTINGS', silent=True)


### helper functions ###
def pandoc_convert(string):
    args = ['pandoc', '-t', 'html5', '--mathjax', '--smart']
    p = Popen(args, stdin = PIPE, stdout = PIPE)
    out, err = p.communicate(input=bytes(string, 'UTF-8'))
    return out.decode('UTF-8')

def connect_db():
    """Connects to the specific database. Returns the connection."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context. Returns the connection (new or existing).
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


## static resources ###

@app.route('/')
def root():
    return app.send_static_file('index.html')

### restful api ###

@app.route('/logs', methods=['GET'])
def get_logs():
    db = get_db()

    logs = Log.get_all_entries(db)

    for log in logs:
        log['body'] = pandoc_convert(log['body'])
        log['tags'] = Tag.get_log_tag_names(db, log['id'])

    return jsonify({ 'logs': logs})


@app.route('/logs/<int:id>', methods=['GET'])
def get_log(id):
    db = get_db()

    log = Log.get_entry(db, id)

    if log is None:
        abort(404)

    log['body'] = pandoc_convert(log['body'])
    log['tags'] = Tag.get_log_tag_names(db, log['id'])

    return jsonify({ 'log': log})



@app.route('/logs/', methods=['POST'])
def add_log():
    db = get_db()

    if not request.json or not 'name' in request.json:
        abort(400)

    cur = db.execute('insert into logs (body, ts) values (?, ?)',
                 [request.form['body'], round(time.time())])

    logid = cur.lastrowid

    tags = request.json['tags'].split()
    for tag in tags:
        t = tag[1:]
        cur = db.execute('select id from tags where name = ?', [t])

        if cur.fetchone() == None:
            cur = db.execute('insert into tags (name) values (?)', [t])

        db.execute('insert into logs_tags_assoc (logid, tagid) values (?, ?)', 
                [logid, cur.lastrowid])

    db.commit()
    return jsonify({'id': logid}), 201


@app.route('/logs/<int:id>', methods=['PUT'])
def update_log(id):
    db = get_db()

    if not Log.entry_exists(id):
        abort(404)

    if not request.json:
        abort(400)

    cur = db.execute('update logs set body=? where id=?',
                 [request.json['body'], id])


    tags = request.json['tags'].split()
    new_tags = set()
    for tag in tags:
        t = tag[1:]
        cur = db.execute('select id from tags where name = ?', [t])

        fetch = cur.fetchone()
        if fetch == None:
            cur = db.execute('insert into tags (name) values (?)', [t])
            new_tags.add(cur.lastrowid)
        else:
            new_tags.add(fetch[0])

    cur = db.execute("select tagid from logs_tags_assoc where logid = ?", 
                     [id])
    fetch = cur.fetchall()
    old_tags = set([tag[0] for tag in fetch])

    intersection = new_tags & old_tags
    add_tags = new_tags - intersection
    remove_tags = old_tags - intersection

    for tag in remove_tags:
        db.execute('delete from logs_tags_assoc where logid=? and tagid=?',
                    [id, tag])

    for tag in add_tags:
        db.execute('insert into logs_tags_assoc (logid, tagid) values (?, ?)', 
                   [id, tag])

    db.commit()
    return jsonify({'result': True})


@app.route('/pages', methods=['GET'])
def get_pages():
    db = get_db()

    pages = Page.get_all_pages(db)

    for page in pages:
        page['body'] = pandoc_convert(page['body'])
        page['tags'] = Tag.get_page_tag_names(db, page['id'])

    return jsonify({ 'pages': pages})

@app.route('/pages/<int:id>', methods=['GET'])
def get_page(id):
    db = get_db()

    page = Page.get_entry(db, id)

    if page is None:
        abort(404)

    page = dict(page)
    page['tags'] = Tag.get_page_tag_names(db, page['id'])

    return jsonify({ 'page': page})


@app.route('/pages/', methods=['POST'])
def add_page():
    db = get_db()

    if not request.json or not 'name' in request.json:
        abort(400)

    cur = db.execute('insert into pages (name, slug, body) values (?, ?, ?)',
                 [request.json['name'], slugify(request.json['name']), request.json['body']])

    pageid = cur.lastrowid

    tags = request.json['tags'].split()
    for tag in tags:
        t = tag[1:]
        cur = db.execute('select id from tags where name = ?', [t])

        if cur.fetchone() == None:
            cur = db.execute('insert into tags (name) values (?)', [t])

        db.execute('insert into pages_tags_assoc (pageid, tagid) values (?, ?)', 
                [pageid, cur.lastrowid])

    db.commit()
    return jsonify({'id': pageid}), 201


@app.route('/pages/<int:id>', methods=['PUT'])
def update_page(id):
    db = get_db()

    if not Page.page_exists(id):
        abort(404)

    if not request.json:
        abort(400)

    cur = db.execute('update pages set name=?, body=?, slug=? where id=?',
                 [request.json['name'], request.json['body'], 
                  slugify(request.json['name']), id])


    tags = request.json['tags'].split()
    new_tags = set()
    for tag in tags:
        t = tag[1:]
        cur = db.execute('select id from tags where name = ?', [t])

        fetch = cur.fetchone()
        if fetch == None:
            cur = db.execute('insert into tags (name) values (?)', [t])
            new_tags.add(cur.lastrowid)
        else:
            new_tags.add(fetch[0])

    cur = db.execute("select tagid from pages_tags_assoc where pageid = ?", 
                     [id])
    fetch = cur.fetchall()
    old_tags = set([tag[0] for tag in fetch])

    intersection = new_tags & old_tags
    add_tags = new_tags - intersection
    remove_tags = old_tags - intersection

    for tag in remove_tags:
        db.execute('delete from pages_tags_assoc where pageid=? and tagid=?',
                    [id, tag])

    for tag in add_tags:
        db.execute('insert into pages_tags_assoc (pageid, tagid) values (?, ?)', 
                   [id, tag])

    db.commit()
    return jsonify({'result': True})


@app.route('/pages/<int:id>', methods=['DELETE'])
def delete_page(id):
    db = get_db()

    cur = db.execute('select id, name, slug, body from pages where id=?', [id])
    page = cur.fetchone()

    if page is None:
        abort(404)

    cur = db.execute('delete from pages where id=?', [id])
    db.commit()
    return jsonify({'result': True})



if __name__ == '__main__':
    app.run()
