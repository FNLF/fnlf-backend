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
from ext.melwin.melwin import Melwin
from ext.app.eve_helper import eve_response, eve_abort

# TIME & DATE - better with arrow only?
import arrow
# Auth, not needed since token based
from time import sleep
import sys

# Token generation
from uuid import uuid4
# Convenience - provide a base 64 encoded token
from base64 import b64encode

from ext.app.decorators import *

Authenticate = Blueprint('Authenticate', __name__, )


@Authenticate.route("/authenticate", methods=['POST'])
# @track_time_spent('authenticate')
def login():
    username = None
    password = None

    m = Melwin()

    # Request via json
    rq = request.get_json()

    # Only integers for Melwin:
    try:
        username = int(rq['username'])
        password = rq['password']
    except:
        # Now it will fail in the next if
        pass

        # if request.form.get('username',type=int) == 45199 and request.form.get('password',type=int) == 45199:
    # if m.login(request.form.get('username',type=int), request.form.get('password',type=int)):
    if isinstance(username, int) and len(password) == 9 and m.login(username, password):

        # app = current_app._get_current_object()

        from eve.methods.post import post_internal
        # Will not work due to some If-Match stuff 
        # from eve.methods.patch import patch_internal

        _id = None
        _etag = None

        # Find existing:
        try:
            accounts = app.data.driver.db[app.globals['auth']['auth_collection']]
            user = accounts.find_one({'id': username})

        except:
            user = None
            eve_abort(500, 'Something went wrong, we do not know what yet but admin is alerted')

        # If not existing, make from melwin!
        if not user:
            melwin_api = app.data.driver.db['melwin_users']
            melwin_user = melwin_api.find_one({'id': username})

            if melwin_user:

                # NB set up acl!
                acl = {'groups': [],
                       'roles': []}

                try:  # Users
                    r_user = post_internal(app.globals['auth']['users_collection'], {'id': melwin_user['id'], 'acl': acl}, skip_validation=True)

                except:
                    eve_abort(500, 'Something went wrong with your user update from membership system')

                try:  # Users auth collection
                    users_auth_collection = app.data.driver.db[app.globals['auth']['auth_collection']]
                    r_auth = users_auth_collection.insert({'id': melwin_user['id'], 'user': r_user[0]['_id'], 'auth': {"token": "", "valid": ""}})
                    _id = r_auth

                except pymongo.errors.ServerSelectionTimeoutError as mongoerr:
                    eve_abort(503, 'The server experienced network timeout problems', mongoerr)
                except:
                    eve_abort(500, 'Something went wrong with your user authentication setup')

        else:
            _id = user['_id']
            # _etag = user['_etag']

        # If login, generate new token and valid to datetime
        token = uuid4().hex

        # Make token valid to
        utc = arrow.utcnow()
        valid = utc.replace(hours=+2)  # @bug: utc and cet!!!

        try:
            # r = patch_internal('users_auth', payload={'auth': {'token': token, 'valid': valid.datetime}}, concurrency_check=False, **{'_id': _id})
            # last = app.data.update(app.globals['auth']['auth_collection'], _id, {"$set": {'auth': {'token': token, 'valid': valid.datetime}}}) #resource, id_, updates

            # Wont work with the update or patch_internal or any other internal for now
            accounts = app.data.driver.db[app.globals['auth']['auth_collection']]
            accounts.update({'_id': _id}, {"$set": {"auth.token": token, "auth.valid": valid.datetime}})

        except pymongo.errors.ServerSelectionTimeoutError as mongoerr:
            eve_abort(503, 'The server experienced network timeout problems', mongoerr)
        except:
            eve_abort(500, 'Something went wrong setting your authentication token')

        # Base 64 for reuse
        t = '%s:' % token
        b64 = b64encode(t.encode())

        # token = uuid5(uuid4(),rq['username'])
        # when authentication your application needs to supply the authentication token
        # for each request valid to sets to say 1h future
        # lookup is on auth token, then user etc
        # This will be the one auth to send to Eve?
        # Only jsonify seems to work? The base64 token is it?
        return jsonify(**{'success': True,
                          'token': token,
                          'token64': b64,
                          'valid': valid.datetime,
                          '_id': str(_id)})
        return eve_response({'success': True,
                             'token': token,
                             'token64': b64,
                             'valid': valid.datetime,
                             '_id': str(_id)})

    # On error sleep a little against brute force
    sleep(1)
    # return jsonify(**{'success': False, 'token': None, 'message': 'Wrong username or password'})
    return eve_response({'success': False, 'token': None, 'message': 'Wrong username or password'})


"""
A simple whoami
"""


@Authenticate.route("/self", methods=['GET'])
@require_token()
def get_user():
    # app = current_app._get_current_object()
    try:
        col = app.data.driver.db['users']
        user = col.find_one({'id': app.globals['id']})

        if user:
            return jsonify(**{'whoami': app.globals['id']})
    except pymongo.errors.ServerSelectionTimeoutError as mongoerr:
        eve_abort(503, 'The server experienced network timeout problems', mongoerr)
    except:
        eve_abort(500, 'Unknown error occurred')
