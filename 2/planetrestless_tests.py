import requests
import json

# flask-restless doesn't support unit testing very nicely, so we'll do functional testing with `requests` instead

prefix = 'http://localhost:5000'

headers = {'Content-Type': 'application/json'}

def get_user(userid='testguy'):
    return requests.get(prefix + '/users/' + userid, headers=headers)

def create_user(first_name='test', last_name='guy', userid='testguy', groups=['testgroup']):
    return requests.post(prefix + '/users',
                         data=json.dumps({'first_name': first_name, 'last_name': last_name, 'userid': userid, 'groups': groups}),
                         headers=headers)

def delete_user(userid='testguy'):
    return requests.delete(prefix + '/users/' + userid)

def update_user(first_name='test', last_name='guy', userid='testguy', groups=['testgroup']):
    return requests.put(prefix + '/users/' + userid,
                        data=json.dumps({'first_name': first_name, 'last_name': last_name, 'userid': userid, 'groups': groups}),
                        headers=headers)

def get_group(group_name='testgroup'):
    return requests.get(prefix + '/groups/' + group_name, headers=headers)

def create_group(group_name='testgroup'):
    return requests.post(prefix + '/groups', data=json.dumps({'group_name': group_name}), headers=headers)

def update_group(group_name='testgroup', users=['testuser']):
    return requests.put(prefix + '/groups/' + group_name, data=json.dumps({'users': users}), headers=headers)

def delete_group(group_name='testgroup'):
    return requests.delete(prefix + '/groups/' + group_name, headers=headers)

# Delete testguy and testgroup if they exist
try:
    delete_user()
except:
    pass

try:
    delete_group()
except:
    pass

# user should not exist
r = get_user()
assert '404' in str(r.status_code)

# create user
r = create_user()
assert '201' in str(r.status_code)
r = get_user()
assert '200' in str(r.status_code)
assert 'testguy' in r.text

# check user membership
assert 'testgroup' in r.text

# try creating a duplicate user - this should fail
r = create_user()
assert '409' in str(r.status_code)

# create a different user
r = create_user('firstname', 'lastname', 'testuser2')
r = get_user('testuser2')
assert '200' in str(r.status_code)
assert 'testuser2' in str(r.text)
delete_user('testuser2')

# delete the test user
r = delete_user()
assert '204' in str(r.status_code)
r = get_user()
assert '404' in str(r.status_code)

# attempt to delete the user again
r = delete_user()
assert '404' in str(r.status_code)

# recreate the user for further tests
r = create_user()

# test update/PUT
r = update_user('newfirst', 'newlast', 'testguy')
assert '200' in str(r.status_code)
r = get_user()
assert 'newfirst' in r.text

# test PUT with groups
r = update_user('test', 'guy', 'testguy', groups=['testgroup1'])
r = get_user()
assert 'testgroup1' in r.text

# test PUT on nonexistant user - should return 404
r = update_user('', '', 'nonexistant')
assert '404' in str(r.status_code)

# test create_group
delete_group()
r = create_group()
assert '201' in str(r.status_code)
r = get_group()
assert '200' in str(r.status_code)

# test delete group
delete_group()
r = get_group()
assert '404' in str(r.status_code)

# test delete nonexistant group
r = delete_group()
assert '404' in str(r.status_code)

# test create duplicate group - should fail with 409
r = create_group()
r = create_group()
assert '409' in str(r.status_code)

# ensure a group that doesnt exist returns 404
r = get_group('nonexistant')
assert '404' in str(r.status_code)

# test update group
create_group()
r = update_group('testgroup', [])
assert '200' in str(r.status_code)
assert 'testguy' not in r.text
r = update_group('testgroup', ['testguy'])
assert '200' in str(r.status_code)
assert 'testguy' in r.text


# clean up
delete_user()
delete_group()
