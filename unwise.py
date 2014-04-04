import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup

from subprocess import Popen, PIPE

def pandoc_convert(string):
    args = ['pandoc', '-t', 'html5', '--mathjax', '--smart']
    p = Popen(args, stdin = PIPE, stdout = PIPE)
    out, err = p.communicate(input=bytes(string, 'UTF-8'))
    print("===========Converting=============\n\n")
    print(string)
    print("\n\n")
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
def show_entries():
    db = get_db()
    cur = db.execute('select name, body from entries order by id desc')
    entries = cur.fetchall()

    entries = [dict(entry) for entry in entries]

    for entry in entries:
        entry['body'] = pandoc_convert(entry['body'])

    print("AAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHHHHHHH")
    print(entries)
    
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into entries (name, body) values (?, ?)',
                 [request.form['name'], request.form['body']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
