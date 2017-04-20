"""
    Token based Auth
    ================
    
    Also ACL added!!
    
    @attention: Needs tokenmaster to issue tokens
"""

# Atuhentication
from flask import current_app as app, request, Response, abort
from eve.auth import TokenAuth
from eve.methods.patch import patch_internal
from eve.methods.get import getitem_internal, get_internal
# from bson.objectid import ObjectId
from ext.auth.helpers import Helpers
import arrow

class TokenAuth(TokenAuth):
    
    is_auth = False
    user_id = None
    
    
    def check_auth(self, token, allowed_roles, resource, method):
        """Simple token check. Tokens comes in the form of request.authorization['username']
        Token is decoded request.authorization['username']
        """
        # Needs to check token exists and equals request AND valid is in the future!
        # Token expired error
        # Token error
        # Set acl to the global XXX for use in all pre_ db lookup queries!
        # Can also get the database lookup for the resource and check that here!!
        # Can also issue a new token here, and that needs to be returned by injecting to pre dispatch
        # use the abort/eve_error_msg to issue errors!


        user, _, _, status = getitem_internal(resource='users/auth', **{'auth.token': token})

        if '_id' in user and status == 200:

            self.user_id = user['id']

            utc = arrow.utcnow()
            if utc.timestamp < arrow.get(user['auth']['valid']).timestamp:

                valid = utc.replace(hours=+1)
                
                # If it fails, then token is not renewed
                #accounts.update_one({'_id': u['_id']}, {"$set": {"auth.valid": valid.datetime}})

                response, _, _, status = patch_internal('users/auth',
                                                                       payload={
                                                                           'auth': {'valid': valid.datetime}},
                                                                       concurrency_check=False, **{'_id': user['_id']})
                
                # For use in pre_insert/update - handled in set_acl
                #app.globals.update({'id': u['id']})
                #app.globals.update({'_id':  u['_id']})
                
                # Set acl
                app.globals.update({'user_id': user['id']})
                #self.set_acl(u['acl'], u['_id'], u['id'])
                self._set_globals(user['id'], user['user'])
                
                #Set acl - use id to make sure
                self.set_acl(user['id'])

                # See if needed for the resource
                # Contains per method (ie read or write or all verbs)
                if allowed_roles:

                    helper = Helpers()
                    local_roles = []
                    for role in allowed_roles:
                        local_roles.extend(helper.get_all_users_in_role_by_ref(ref=role))

                    if len(local_roles) == 0 or user['id'] not in local_roles:
                        self.is_auth = False
                        return False


                self.is_auth = True
                
                # Set request auth value IF on users resource
                # This effectively limits all operations except GET
                # hence only the authenticated user can change the corresponding users item (by id)
                # @note: This corresponds to domain definition 'auth_field': 'id'
                if method != 'GET' and resource == 'users':
                    self.set_request_auth_value(user['id'])

                # This allows oplog to push u = id (membership #)
                self.set_user_or_token(user['id'])

                return True # Token exists and is valid, renewed for another hour
            
            else: # Expired validity
                return False

        return False
    
    def get_user_id(self):
        return self.user_id
    
    def _set_globals(self, id, _id):
        app.globals.update({'id': id})
        app.globals.update({'_id': "%s" % _id})
    
    def authenticate(self):
        """ Overridden by NOT returning a WWW-Authenticate header
        This makes the browser NOT fire up the basic auth
        """
        resp = Response(None, 401)
        abort(401, description='Please provide proper credentials', response=resp)
            
    
    def set_acl(self, id):
        """ Sets the acl dict on the current authenticated user
        Needs to get clubs from melwin in order to sport the acl_groups.ref link
        """

        user, _, _, status = getitem_internal(resource='users', **{'id': id})

        acl = user['acl']

        melwin_user, _, _, status = getitem_internal(resource='melwin/users', **{'id': id})
        clubs = melwin_user['membership']['clubs']
        
        # Then those pescy groups from clubs!
        groups, _, _, status, _ = get_internal(resource='acl/groups', **{'ref': {'$in': clubs}})
        print(groups)

        for key, _id in enumerate(g['_id'] for g in groups['_items']):
            acl['groups'].append(_id)
        
        acl['groups'] = list(set(acl['groups']))
        acl['roles'] = list(set(acl['roles']))
            
        app.globals.update({'acl': acl})

    def _set_acl(self, acl, _id, id):
        
        if acl:
            app.globals.update({'acl': acl})
            
        raise NotImplemented