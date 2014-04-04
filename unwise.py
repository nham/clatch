import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup

from subprocess import Popen, PIPE

def pandoc_convert(string):
    args = ['pandoc', '-t', 'html5', '--mathjax', '--smart']
    p = Popen(args, stdin = PIPE, stdout = PIPE)
    out, err = p.communicate(input=bytes(string, 'UTF-8'))
    return out.decode('UTF-8')


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


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def show_pages():
    db = get_db()
    cur = db.execute('select name, body from pages order by id desc')
    pages = cur.fetchall()

    pages = [dict(page) for page in pages]

    for page in pages:
        page['body'] = pandoc_convert(page['body'])

    return render_template('show_pages.html', pages=pages)

@app.route('/add', methods=['POST'])
def add_page():
    db = get_db()

    cur = db.execute('insert into pages (name, body) values (?, ?)',
                 [request.form['name'], request.form['body']])

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
    return redirect(url_for('show_pages'))

if __name__ == '__main__':
    app.run()
