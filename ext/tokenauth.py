"""
    Token based Auth
    ================
    
    Also ACL added!!
    
    @attention: Needs tokenmaster to issue tokens
"""

# Atuhentication
from eve.auth import TokenAuth

from flask import current_app as app, request, Response, abort

# TIME & DATE - better with arrow only?
import arrow

class TokenAuth(TokenAuth):
    
    is_auth = False
    
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
        print("=============================================================")
        accounts = app.data.driver.db[app.globals['auth']['auth_collection']]
        
        u = accounts.find_one({'auth.token': token})
        print(u)
        if u:
            utc = arrow.utcnow()
            if utc.timestamp < arrow.get(u['auth']['valid']).timestamp:

                valid = utc.replace(hours=+1)
                
                # If it fails, then token is not renewed
                accounts.update({'_id': u['_id']}, { "$set": { "auth.valid": valid.datetime } } )
                
                # For use in pre_insert/update - handled in set_acl
                #app.globals.update({'id': u['id']})
                #app.globals.update({'_id':  u['_id']})
                
                # Set acl
              
                #self.set_acl(u['acl'], u['_id'], u['id'])
                self._set_globals(u['id'], u['_id'])
                self.is_auth = True
                return True # Token exists and is valid, renewed for another hour
            
            else: # Expired validity
                return False
        else: # No token in database
            return False
    
    def _set_globals(self, id, _id):
        app.globals.update({'id': id})
        app.globals.update({'_id': "%s" % _id})
        print("App.globals")
        print(app.globals)    
    
    def authenticate(self):
        """ Overridden by NOT returning a WWW-Authenticate header
        This makes the browser NOT fire up the basic auth
        """
        resp = Response(None, 401)
        abort(401, description='Please provide proper credentials', response=resp)
            
    """
        Set ACL
        =======
        
        Sets the acl dict on current user including needed information!
    """
    def _set_acl(self, acl, _id, id):
        if acl:
            app.globals.update({'acl': acl})
        print("App.globals")
        print(app.globals)
        
        