import os, planetrest, unittest, tempfile
from flask import json

class PlanetRestTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, planetrest.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = planetrest.app.test_client()
        planetrest.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(planetrest.app.config['DATABASE'])

    def get_user(self, userid='testguy'):
        return self.app.get('/users/' + userid)

    def test_user_should_not_exist(self):
        r = self.get_user('nonexistant')
        assert '404' in r.status

    def create_user(self, first_name='test', last_name='guy', userid='testguy', groups=['testgroup']):
        # convert the dict to a string of json and set content_type because http://werkzeug.pocoo.org/docs/0.11/test/#testing-api
        return self.app.post('/users', data=json.dumps(dict(
            first_name=first_name, last_name=last_name, userid=userid, groups=groups)),
                             content_type='application/x-www-form-urlencoded')

    def test_create_user_invalid_fields(self):
        r = self.create_user('', '', '')  # empty userid is invalid
        assert '400' in r.status

    def test_create_user(self):
        r = self.create_user()
        assert '204' in r.status
        r = self.get_user()
        assert '200' in r.status

    def test_create_user_groups(self):
        r = self.create_group()
        r = self.create_user()
        r = self.get_user()
        assert 'testgroup' in r.data

    def test_create_user_duplicate(self):
        r = self.create_user()
        r = self.create_user()
        assert '409' in r.status

    def delete_user(self, userid='testguy'):
        return self.app.delete('/users/' + userid)

    def test_delete_user_nonexistant(self):
        r = self.delete_user('nonexistant')
        assert '404' in r.status

    def test_delete_user(self):
        r = self.create_user()
        r = self.delete_user()
        assert '204' in r.status
        r = self.get_user()
        assert '404' in r.status

    def update_user(self, first_name='test', last_name='guy', userid='testguy', groups=['testgroup']):
        return self.app.put('/users/' + userid, data=json.dumps(dict(
            first_name=first_name, last_name=last_name, groups=groups)),
                            content_type='application/x-www-form-urlencoded')

    def test_update_user(self):
        r = self.create_user()
        r = self.update_user('test1', 'guy1', 'testguy')
        assert '204' in r.status
        r = self.get_user()
        assert 'test1' in r.data

    def test_update_user_groups(self):
        r = self.create_user()
        r = self.create_group()
        r = self.create_group('some_other_group')
        r = self.update_user('test', 'guy', 'testguy', ['testgroup',
                                                        'some_other_group'])
        r = self.get_user('testguy')
        assert '200' in r.status
        assert 'testgroup' in r.data
        assert 'some_other_group' in r.data

    def test_update_user_groups_overwrite(self):
        r = self.create_user()
        r = self.create_group()
        r = self.create_group('some_other_group')
        r = self.update_user('test', 'guy', 'testguy', ['testgroup',
                                                        'some_other_group'])
        r = self.get_user('testguy')
        assert 'testgroup' in r.data
        assert 'some_other_group' in r.data
        r = self.update_user('test', 'guy', 'testguy', ['testgroup'])
        r = self.get_user('testguy')
        assert 'testgroup' in r.data
        assert 'some_other_group' not in r.data

    def test_update_user_nonexistant_user(self):
        r = self.update_user('test2', 'guy2', 'nonexistant')
        assert '404' in r.status
 
    def create_group(self, name='testgroup'):
        return self.app.post('/groups', data=json.dumps(dict(name=name)),
                             content_type='application/x-www-form-urlencoded')

    def get_group(self, group_name='testgroup'):
        return self.app.get('/groups/' + group_name)

    def test_create_group(self):
        r = self.create_group()
        assert '201' in r.status

    def test_create_group_invalid_name(self):
        r = self.create_group('')  # empty name is invalid
        assert '400' in r.status

    def test_create_group_duplicate(self):
        r = self.create_group()
        r = self.create_group()
        assert '409' in r.status

    def test_get_group_nonexistant(self):
        r = self.get_group('nonexistant')
        assert '404' in r.status

    def test_get_group(self):
        r = self.create_group()
        r = self.get_group()
        assert '200' in r.status

    def update_group(self, group_name='testgroup', users=['testguy']):
        return self.app.put('/groups/' + group_name,
                            data=json.dumps(users),
                            content_type='application/x-www-form-urlencoded')

    def test_update_group_nonexistant_group(self):
        r = self.update_group('nonexistant', [])
        assert '404' in r.status

    def test_update_group(self):
        r = self.create_user()
        r = self.create_group()
        r = self.update_group()
        r = self.get_group()
        assert '200' in r.status
        assert 'testguy' in r.data

    def test_update_group_invalid_request(self):
        r = self.create_group()
        r = self.app.put('/groups/testgroup', data='not_valid_json')
        assert '400' in r.status

    def delete_group(self, group_name='testgroup'):
        return self.app.delete('/groups/' + group_name)

    def test_delete_group_nonexistant(self):
        r = self.delete_group()
        assert '404' in r.status

    def test_delete_group(self):
        r = self.create_group()
        r = self.delete_group()
        assert '204' in r.status
        r = self.get_group()
        assert '404' in r.status

    def test_delete_group_membership_fk_constraint(self):
        r = self.create_user()
        r = self.create_group()
        r = self.update_group()
        r = self.delete_group()
        assert 'testguy' not in r.data


if __name__ == '__main__':

    unittest.main()
