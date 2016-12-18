"""
Simple helpers

groups = col = app.data.driver.db['acl_groups']
roles = app.data.driver.db['acl_roles']
reporter = self.db_wf.get('reporter')
        


"""

from flask import current_app as app
from bson.objectid import ObjectId


class Helpers():
    def get_user_id(self):
        return app.globals['user_id']

    def get_user_name(self, id):

        melwin = app.data.driver.db['melwin_users']
        user = melwin.find_one({'id': id}, {'firstname': 1, 'lastname': 1})

        return '%s %s' % (user['firstname'], user['lastname'])

    def get_users_from_groups(self, groups):
        """ Returns all user id's in group (objectid)
        """

        users = app.data.driver.db['users']
        r = list(users.find({'acl.groups': {'$in': groups}}))

        l = []
        for u in r:
            l.append(u['id'])

        return list(set(l))

    def get_users_from_roles(self, roles):
        """ Returns list of all user id's with roles (objectid)
        """

        users = app.data.driver.db['users']
        r = list(users.find({'acl.roles': {'$in': roles}}))

        l = []
        for u in r:
            l.append(u['id'])

        return list(set(l))

    def get_users_hi(self, club):
        """ Return all user id's of role hi in club
        """

        role = self.get_role_hi(club)
        users = app.data.driver.db['users']
        r = list(users.find({'acl.roles': {'$in': [role]}}))

        hi = []
        for u in r:
            hi.append(u['id'])

        return list(set(hi))

    def get_users_su(self):
        """ Return list og all user id's in group su
        """
        group = self.get_group_su()
        users = app.data.driver.db['users']
        r = list(users.find({'acl.groups': {'$in': [group]}}))
        su = []
        for u in r:
            su.append(u['id'])

        return list(set(su))

    def get_users_fs(self):
        """ Returns list of all user id's with role fs
        """
        role = self.get_role_fs()
        users = app.data.driver.db['users']
        r = list(users.find({'acl.roles': {'$in': [role]}}))

        fs = []
        for u in r:
            fs.append(u['id'])

        return list(set(fs))

    def get_role_hi(self, club):
        """ Returns the role id of hi in club
        """

        roles = app.data.driver.db['acl_roles']

        r = roles.find_one({"ref": 'hi', 'group': ObjectId(self.get_group_club(club))})

        if r and r.get('_id', False):
            return r['_id']
        else:
            return None

    def get_group_su(self):
        """ Returns the group id of the su group
        """
        groups = app.data.driver.db['acl_groups']

        group = groups.find_one({'ref': 'su'})

        if '_id' in group:
            return group['_id']
        else:
            return None

    def get_role_fs(self):
        """ Return the role id of the role fs
        """
        roles = app.data.driver.db['acl_roles']
        role = roles.find_one({'ref': 'fs'})

        if '_id' in role:
            return role['_id']
        else:
            return None

    def get_superadmins(self):
        """ Return the role id of the role fs
        """
        roles = app.data.driver.db['acl_roles']
        role = roles.find_one({'ref': 'superadmin'})

        if '_id' in role:
            return self.get_users_from_roles([role['_id']])
        else:
            return None


    def get_group_club(self, club):

        groups = app.data.driver.db['acl_groups']

        group = groups.find_one({'ref': club})

        if '_id' in group:
            return group['_id']
        else:
            return None

    def get_all_groups(self):

        groups = app.data.driver.db['acl_groups']

        return list(groups.find())

    def get_all_clubs(self):

        groups = app.data.driver.db['melwin_clubs']

        return list(groups.find())

    def get_melwin_users_email(self, users):
        """ Returns a list of tuples (name, email) from a list of user id'
        """

        if len(users) == 0:
            return []

        users = list(map(int, users))

        melwin = app.data.driver.db['melwin_users']
        r = list(melwin.find({'id': {'$in': users}}, {'id': 1, 'firstname': 1, 'lastname': 1, 'email': 1}))

        mu = []
        for u in r:
            mu.append({'name': '%s %s' % (u['firstname'], u['lastname']), 'email': u['email'], 'id': u['id']})

        return mu

    def get_melwin_users_phone(self, users):
        """ Returns a list of tuples (name, phone) from a list of user id'
        """
        users = app.data.driver.db['users_melwin']
        r = list(users.find({'id': {'$in': users}}, {'firstname': 1, 'lastname': 1, 'phone': 1}))
        mu = []
        for u in r:
            mu.append({'name': '%s %s' % (u['firstname'], u['lastname']), 'phone': u['phone'], 'id': u['id']})

        return mu

    def get_melwin_club_name(self, club):
        melwin = app.data.driver.db['melwin_clubs']
        c = melwin.find_one({'id': club}, {'name': 1})

        if 'name' in c:
            return c['name']
        else:
            return None

    def collect_users(self, users=[], roles=[], groups=[]):

        if not users:
            users = []

        try:
            r = self.get_users_from_roles(roles)
            g = self.get_users_from_groups(groups)

            if len(r) > 0:
                users.extend(r)
            if len(g) > 0:
                users.extend(g)

            return list(set(users))
        except:
            return []
