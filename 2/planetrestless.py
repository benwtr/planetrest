import flask
import flask.ext.sqlalchemy
import flask.ext.restless
from flask.ext.restless import ProcessingException

app = flask.Flask(__name__)
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/planetrestless.db'

db = flask.ext.sqlalchemy.SQLAlchemy(app)

# Normally I would have given these tables an autoincrement id column but I wanted to use
# compound foreign keys and sqlite disables autoincrement when using compound FKs

Groups = db.Table('groups',
                  db.Column('userid', db.Unicode, db.ForeignKey('user.userid')),
                  db.Column('group_name', db.Unicode, db.ForeignKey('group.group_name')))

class User(db.Model):
    userid = db.Column(db.Unicode, primary_key=True)
    first_name = db.Column(db.Unicode)
    last_name = db.Column(db.Unicode)
    groups = db.relationship('Group', secondary=Groups,
                             backref=db.backref('users', lazy='dynamic'))

class Group(db.Model):
    group_name = db.Column(db.Unicode, primary_key=True)

db.create_all()

manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

def post_get_user(result=None, **kw):
    grouplist = []
    for group_name in result['groups']:
        grouplist.append(group_name.values()[0])
    result['groups'] = grouplist

def pre_put_user(data=None, **kw):
    grouplist = []
    for group_name in data['groups']:
        grouplist.append(dict({'group_name': group_name}))
    data['groups'] = grouplist

def pre_create_user(data=None, **kw):
    # It would have been cleaner to catch IntegrityError from sqlalchemy for
    # the duplicate record instead of this extra hit to the DB but it probably
    # would have meant monkey patching flask-restless
    if User.query.filter_by(userid=data['userid']).first():
        raise ProcessingException(description='Duplicate record', code=409)
    grouplist = []
    for group_name in data['groups']:
        grouplist.append(dict({'group_name': group_name}))
    data['groups'] = grouplist

manager.create_api(User, methods=['GET', 'POST', 'PUT', 'DELETE'], collection_name='users',
                   url_prefix='',
                   preprocessors={
                       'PUT_SINGLE': [pre_put_user],
                       'POST': [pre_create_user]
                   },
                   postprocessors={
                       'GET_SINGLE': [post_get_user],
                       'PUT_SINGLE': [post_get_user],
                       'POST': [post_get_user]
                   })

def post_get_group(result=None, **kw):
    userlist = []
    for userid in result['users']:
        userlist.append(userid.values()[0])
    result['users'] = userlist

def pre_put_group(data=None, **kw):
    userlist = []
    for userid in data['users']:
        userlist.append(dict({'userid': userid}))
    data['users'] = userlist

def pre_create_group(data=None, **kw):
    if Group.query.filter_by(group_name=data['group_name']).first():
        raise ProcessingException(description='Duplicate record', code=409)


manager.create_api(Group, methods=['GET', 'POST', 'PUT', 'DELETE'], collection_name='groups',
                   exclude_columns=['users.first_name', 'users.last_name'],
                   url_prefix='',
                   preprocessors={
                       'PUT_SINGLE': [pre_put_group],
                       'POST': [pre_create_group]
                   },
                   postprocessors={
                       'GET_SINGLE': [post_get_group],
                       'PUT_SINGLE': [post_get_group],
                       'POST': [post_get_group]}
                  )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

