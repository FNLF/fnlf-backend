"""
    Simple authentication 
    =====================
    
    Should really return a authentication token to be used for the session
    methods=['POST']
    
    from pprint import pprint
    pprint(request.form.get('username'))
    pprint(request.form.get('password'))
    
"""
from flask import Blueprint, current_app as app, request, Response, abort, jsonify
from ext.melwin import Melwin
# Debug
from pprint import pprint
# TIME & DATE - better with arrow only?
import arrow
# Auth, not needed since token based
from time import sleep

# Token generation
from uuid import uuid4
# Convenience - provide a base 64 encoded token
from base64 import b64encode

from ext.decorators import *

import datetime



Authenticate = Blueprint('Authenticate', __name__,)

@Authenticate.route("/authenticate", methods=['POST'])
@track_time_spent('authenticate')
def login():
    
    username = None
    password = None
    
    m = Melwin()
    
    # Request via json
    rq = request.get_json()
    
    # Request via basic auth!
    """pprint(request.authorization)
    p = request.get_json()
    pprint(p)
    rq = {}
    rq['username'] = request.authorization['username']
    rq['password'] = request.authorization['password']
    """
    #time.sleep(5)
    
    pprint(rq)
    
    # Cast to integer
    # Only integers for Melwin:
    try:
        username = int(rq['username'])
        password = int(rq['password'])
    except:
        # Now it will fail in the if
        pass  
    
    #if request.form.get('username',type=int) == 45199 and request.form.get('password',type=int) == 45199:
    #if m.login(request.form.get('username',type=int), request.form.get('password',type=int)):
    if isinstance( username, int ) and isinstance( password, int ) and m.login(username, password):
        
        #app = current_app._get_current_object()
        
        from eve.methods.post import post_internal
        # Will not work due to some If-Match stuff 
        #from eve.methods.patch import patch_internal
        
        _id = None
        _etag = None
        
        # Find existing:
        try:
            accounts = app.data.driver.db[app.globals['auth']['auth_collection']]
            user = accounts.find_one({'id': username})
        except:
            user = None
            pprint("Error, did not find any user!")
        
        # If not existing, make from melwin!
        if not user:
            melwin_api = app.data.driver.db['melwin_users']
            melwin_user = melwin_api.find_one({'id': username})
            
            pprint(melwin_user)
            if melwin_user:
                
                try: # Users 
                    r_user = post_internal(app.globals['auth']['users_collection'], {'id': melwin_user['id']})
                    
                except:
                    print("Could not insert users_collection")
                
                try:# Users auth collection
                    users_auth_collection = app.data.driver.db[app.globals['auth']['auth_collection']]
                    r_auth = users_auth_collection.insert({'id': melwin_user['id'], 'user': r_user[0]['_id'], 'auth': {"token": "", "valid": ""}})
                    _id = r_auth
                    
                except:
                    print("Could not insert into auth collection")    
               
        else:
            _id = user['_id']
            #_etag = user['_etag']
        
        # If login, generate new token and valid to datetime
        token = uuid4().hex
        
        # Need to convert to string...
        #_id = "%s" % _id
        
        # Make token valid to
        utc = arrow.utcnow()
        valid = utc.replace(hours=+2) #@bug: utc and cet!!!
        
        try:
            #r = patch_internal('users_auth', payload={'auth': {'token': token, 'valid': valid.datetime}}, concurrency_check=False, **{'_id': _id})
            #last = app.data.update(app.globals['auth']['auth_collection'], _id, {"$set": {'auth': {'token': token, 'valid': valid.datetime}}}) #resource, id_, updates
            
            # Wont work with the update or patch_internal or any other internal for now
            accounts = app.data.driver.db[app.globals['auth']['auth_collection']]
            accounts.update({'_id': _id}, { "$set": {"auth.token": token,"auth.valid": valid.datetime } } )
            
            
        except:
            pprint("Updating didnt work!")
            e = sys.exc_info()[0]
            pprint(e)
            pass
        
        #Base 64 for reuse
        t = '%s:' % token
        b64 = b64encode(t.encode())
        
        #token = uuid5(uuid4(),rq['username'])
        # when authentication your application needs to supply the authentication token
        # for each request valid to sets to say 1h future
        # lookup is on auth token, then user etc
        # This will be the one auth to send to Eve?
        return jsonify(**{'success': True, 
                          'token': token,
                          'token64': b64,
                          'valid': valid.datetime})
    
    # On error sleep a little against brute force
    sleep(1)
    return jsonify(**{'success': False, 'token': None, 'message': 'Wrong username or password'})

"""
A simple whoami
"""
@Authenticate.route("/self", methods=['GET'])
@require_token()
def get_user():
    #app = current_app._get_current_object()
    try:
        col = app.data.driver.db['users']
        user = col.find_one({'id': app.globals['id']})
        
        if user:
            return jsonify(**{'whoami':app.globals['id']})
    except:
        resp = Response(None, 501)
        abort(501, description='Unknown error occurred', response=resp)
    
    
