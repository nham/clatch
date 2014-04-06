import os
import sqlite3
import time
from slugify import slugify # awesome-slugify

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup

from subprocess import Popen, PIPE

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'unwise.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='funky'
))
app.config.from_envvar('UNWISE_SETTINGS', silent=True)


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


### routes ###

@app.route('/')
def show_index():
    db = get_db()

    cur = db.execute('select id, name, slug, body from pages order by id desc')
    pages = cur.fetchall()

    pages = [dict(page) for page in pages]

    for page in pages:
        page['body'] = pandoc_convert(page['body'])

        sql = """
            select name from tags t 
            LEFT JOIN pages_tags_assoc a ON a.tagid = t.id
            where a.pageid=?
        """

        cur = db.execute(sql, [page['id']])
        tags = cur.fetchall()
        page['tags'] = [dict(tag) for tag in tags]


    # log entries
    cur = db.execute('select id, body, ts from logs order by id desc')
    logs = cur.fetchall()

    logs = [dict(log) for log in logs]

    for log in logs:
        log['body'] = pandoc_convert(log['body'])

        sql = """
            select name from tags t 
            LEFT JOIN logs_tags_assoc a ON a.tagid = t.id
            where a.logid=?
        """

        cur = db.execute(sql, [log['id']])
        tags = cur.fetchall()
        log['tags'] = [dict(tag) for tag in tags]

    return render_template('show_index.html', pages=pages, logs=logs)

@app.route('/page/new')
def show_new_page_form():
    db = get_db()
    return render_template('show_new_page_form.html')


@app.route('/page/name/<slug>')
def show_page(slug):
    db = get_db()

    cur = db.execute('select id, name, body from pages where slug=? order by id desc', [slug])
    page = cur.fetchone()

    if page is None:
        return render_template('404.html')

    page = dict(page)

    page['body'] = pandoc_convert(page['body'])

    sql = """
        select name from tags t 
        LEFT JOIN pages_tags_assoc a ON a.tagid = t.id
        where a.pageid=?
    """

    cur = db.execute(sql, [page['id']])
    tags = cur.fetchall()
    page['tags'] = [dict(tag) for tag in tags]

    return render_template('show_page.html', page=page)


@app.route('/page/add', methods=['POST'])
def add_page():
    db = get_db()

    cur = db.execute('insert into pages (name, slug, body) values (?, ?)',
                 [request.form['name'], request.form['body'], slugify(request.form['name'])])

    pageid = cur.lastrowid

    tags = request.form['tags'].split()
    for tag in tags:
        t = tag[1:]
        cur = db.execute('select id from tags where name = ?', [t])

        if cur.fetchone() == None:
            cur = db.execute('insert into tags (name) values (?)', [t])

        db.execute('insert into pages_tags_assoc (pageid, tagid) values (?, ?)', 
                [pageid, cur.lastrowid])


    db.commit()
    flash('New page was successfully posted')
    return redirect(url_for('show_index'))


@app.route('/log/new')
def show_new_log_form():
    db = get_db()
    return render_template('show_new_log_form.html')

@app.route('/log/add', methods=['POST'])
def add_log():
    db = get_db()

    cur = db.execute('insert into logs (body, ts) values (?, ?)',
                 [request.form['body'], round(time.time())])

    logid = cur.lastrowid

    tags = request.form['tags'].split()
    for tag in tags:
        t = tag[1:]
        cur = db.execute('select id from tags where name = ?', [t])

        if cur.fetchone() == None:
            cur = db.execute('insert into tags (name) values (?)', [t])

        db.execute('insert into logs_tags_assoc (logid, tagid) values (?, ?)', 
                [logid, cur.lastrowid])


    db.commit()
    flash('New log was successfully posted')
    return redirect(url_for('show_index'))

if __name__ == '__main__':
    app.run()
