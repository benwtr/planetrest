
import ast
import sqlite3
from flask import Flask, abort, g, jsonify, json, request
from wtforms import Form, TextField, validators

DATABASE = '/tmp/planetrest.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
        db.execute('PRAGMA foreign_keys = ON')
        db.commit()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    pass

@app.route('/users/<userid>')
def get_user(userid):
    user = query_db('SELECT first_name, last_name, userid FROM users WHERE userid = ?',
                    [userid], one=True)
    groups_res = query_db('''
    SELECT group_name FROM users, groups, membership
      WHERE ? = users.userid
      AND membership.group_id = groups.id
      AND membership.user_id = users.id
    ''', [userid])
    groups = []
    for group in groups_res:
        groups.append(str(group[0]))
    if user is None:
        abort(404)
    else:
        return jsonify(first_name=user[0],
                       last_name=user[1],
                       userid=user[2],
                       groups=groups)

def set_user_groups(userid, groups):
    user_id = int(query_db('SELECT id FROM users WHERE userid = ?', [userid], one=True)[0])
    db = get_db()
    db.execute('DELETE FROM membership WHERE user_id = ?', [user_id])
    #db.commit()
    for group in groups:
        db.execute('''
        INSERT INTO membership (user_id, group_id)
          SELECT ?, groups.id FROM groups WHERE groups.group_name=?
        ''', [user_id, group])
        db.commit()

@app.route('/users', methods=['POST'])
def create_user():
    try:
        form = json.loads(dict.keys(request.form)[0])
        db = get_db()
        if form['userid'] == '':
            abort(400)
        db.execute('INSERT INTO users VALUES(NULL, ?, ?, ?)', [
            form['first_name'], form['last_name'], form['userid']])
        db.commit()
        set_user_groups(form['userid'], form['groups'])
        return ('', 204)
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in e[0]:
            abort(409)
    except:
        abort(400)

@app.route('/users/<userid>', methods=['DELETE'])
def delete_user(userid):
    if query_db('SELECT id FROM users WHERE userid = ?', [userid], one=True) is None:
        abort(404)
    else:
        db = get_db()
        db.execute('DELETE FROM users WHERE userid = ?', [userid])
        db.commit()
        return ('', 204)

@app.route('/users/<userid>', methods=['PUT'])
def update_user(userid):
    try:
        form = json.loads(dict.keys(request.form)[0])
    except:
        abort(400)
    if query_db('SELECT id FROM users WHERE userid = ?', [userid], one=True) is None:
        abort(404)
    else:
        db = get_db()
        db.execute('UPDATE users SET first_name=?, last_name=? WHERE userid = ?', [
            form['first_name'], form['last_name'], userid])
        db.commit()
        set_user_groups(userid, form['groups'])
        return ('', 204)

@app.route('/groups/<group_name>')
def get_group_users(group_name):
    if query_db('SELECT id from groups where group_name = ?', [group_name], one=True) is None:
        abort(404)
    else:
        res = query_db('''
        SELECT userid FROM users, groups, membership
          WHERE group_name = ?
          AND users.id=membership.user_id
          AND groups.id=membership.group_id''', [group_name])
        members = []
        for member in res:
            members.append(str(member[0]))
        return json.dumps(members)

@app.route('/groups', methods=['POST'])
def create_group():
    try:
        form = json.loads(dict.keys(request.form)[0])
        name = form['name']
        if name == '':
            abort(400)
    except:
        abort(400)
    try:
        db = get_db()
        db.execute('INSERT INTO groups VALUES(NULL, ?)', [name])
        db.commit()
        return ('', 201)
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in e[0]:
            abort(409)

@app.route('/groups/<group_name>', methods=['PUT'])
def set_group_users(group_name):
    group_id = query_db('SELECT id FROM groups WHERE group_name = ?', [group_name], one=True)
    if group_id is None:
        abort(404)
    else:
        try:
            users = json.loads(dict.keys(request.form)[0])
        except:
            abort(400)
        db = get_db()
        try:
            db.execute('DELETE FROM membership WHERE group_id = ?', [group_id[0]])
            for user in users:
                db.execute('''
                INSERT INTO membership (user_id, group_id)
                  SELECT users.id, groups.id FROM users, groups WHERE userid=? AND group_name=?
                ''', [user, group_name])
            db.commit()
        except sqlite3.OperationalError:
            pass
        return ('', 204)

@app.route('/groups/<group_name>', methods=['DELETE'])
def delete_group(group_name):
    if query_db('SELECT id FROM groups WHERE group_name = ?', [group_name], one=True) is None:
        abort(404)
    else:
        db = get_db()
        db.execute('DELETE FROM groups WHERE group_name = ?', [group_name])
        db.commit()
        return ('', 204)


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5000)
