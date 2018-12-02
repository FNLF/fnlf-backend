"""
    Token authentication 
    =====================
    
    Simple token based authentication - safe and sound.
        
"""

from flask import Blueprint, current_app as app, request, Response, abort, jsonify
from eve.methods.post import post_internal
from eve.methods.patch import patch_internal
from eve.methods.get import getitem_internal
from ext.melwin.melwin import Melwin
from ext.app.eve_helper import eve_abort, eve_response, is_mongo_alive
import datetime
import arrow
from time import sleep
from uuid import uuid4
from base64 import b64encode
import traceback
from ext.app.decorators import require_token

# Token auth - oauth
import jwt
ISSUER = 'nlf-auth-server'
JWT_LIFE_SPAN = 1800
REALM = 'mi.nif.no'

Authenticate = Blueprint('Authenticate', __name__, )
import os.path

def _get_public_key():
    public_key = None
    if os.path.isfile('ors-public.pem'):
        print('Exists')

    with open('ors-public.pem', 'rb') as f:
        print('IN file reading wee')
        public_key = f.read()
    return public_key


def create_user(username):

    melwin_user, _, _, status = getitem_internal(resource='melwin/users', **{'id': username})

    if melwin_user and status == 200:

        try:
            user_response, _, _, user_code, header = post_internal(resource=app.globals['auth']['users_collection'],
                                                                   payl={'id': username},
                                                                   skip_validation=True)
        except:
            app.logger.exception("503: Could not create (POST) new user %i" % username)
            return False

        try:
            auth_response, _, _, auth_code, header = post_internal(resource='users/auth',
                                                                   payl={'id': username,
                                                                         'user': user_response['_id'],
                                                                         'auth': {"token": "",
                                                                                  "valid": ""}},
                                                                   skip_validation=True)
        except:
            app.logger.exception("%i: Could not create (mongo insert) user %i auth item" % (auth_code, username))
            return False

        # Verify both post's response codes
        if user_code == 201 and auth_code == 201:
            return True
        else:
            try:
                from eve.methods.delete import deleteitem_internal
                if '_id' in user_response:
                    _, _, _, code = deleteitem_internal(resource=app.globals['auth']['users_collection'],
                                                        concurrency_check=False,
                                                        suppress_callbacks=True,
                                                        **{'_id': user_response['_id']})
                    app.logger.info("Deleted user from users")
                if '_id' in auth_response:
                    _, _, _, code = deleteitem_internal(resource='users/auth',
                                                        concurrency_check=False,
                                                        suppress_callbacks=True,
                                                        **{'_id': auth_response['_id']})
                    app.logger.info("Deleted user from users_auth")
            except:
                app.logger.exception("Delete operation of user %i from users and users_auth but failed" % username)

    return False


@Authenticate.route("/authenticate", methods=['POST'])
def login():
    username = None
    password = None
    logged_in = False

    m = Melwin()

    if m is None:
        app.logger.critical("Melwin service unavailable")
        eve_abort('503', 'Melwin service is unavailable')

    # Request via json
    rq = request.get_json()

    try:
        username = rq['username']
        password = rq['password']
    except:
        # Now it will fail in the next if
        pass


    if username == 'access_token':

        public_key = _get_public_key()
        try:
            decoded_token = jwt.decode(password, public_key, issuer=ISSUER, algorithm='HS256')
            logged_in = True
            username = decoded_token.get('melwin_id', None)
            if username is None:
                eve_abort(401, 'Could not validate the token')
            else:
                username = int(username)

        except (jwt.exceptions.InvalidTokenError,
                jwt.exceptions.InvalidSignatureError,
                jwt.exceptions.InvalidIssuerError,
                jwt.exceptions.ExpiredSignatureError):
            logged_in = False
            eve_abort(401, 'Could not validate the token')

    else:
        try:
            username = int(username)
            logged_in = m.login(username, password)
        except:
            logged_in = False
            eve_abort(503, 'Could not log you into Melwin')

    # isinstance(username, int) and len(password) == 9 and
    if logged_in is True:

        try:
            user, last_modified, etag, status = getitem_internal(resource='users', **{'id': username})
        except:
            user = None
            if not is_mongo_alive():
                eve_abort(502, 'Network problems')

        # If not existing, make from melwin!
        if user is None or status != 200:
            if not create_user(username):
                app.logger.error("502: Could not create user %i from Melwin" % username)
                eve_abort(502, 'Could not create user from Melwin')
            else:
                app.logger.info("Created user %i" % username)

        # token = uuid5(uuid4(),rq['username'])
        token = uuid4().hex

        # valid = utc.replace(hours=+2)  # @bug: utc and cet!!!
        utc = arrow.utcnow()
        valid = utc.replace(seconds=+app.config['AUTH_SESSION_LENGHT'])
        # Pure datetime
        #valid = datetime.datetime.now() + datetime.timedelta(seconds=60)

        try:
            response, last_modified, etag, status = patch_internal('users/auth',
                                                                   payload={'auth': {'token': token, 'valid': valid.datetime}},
                                                                   concurrency_check=False, **{'id': username})
            if status != 200:
                app.logger.error("Could not insert token for %i" % username)

        except:
            app.logger.exception("Could not update user %i auth token" % username)
            eve_abort(500, "Could not update user %i auth token" % username)

        t = '%s:' % token
        b64 = b64encode(t.encode('utf-8'))

        """return jsonify(**{'success': True,
                  'token': token,
                  'token64': b64,
                  'valid': valid,
                  })"""

        return eve_response(data={'success': True,
                                  'token': token,
                                  'token64': b64.decode('utf-8'),
                                  'valid': valid.datetime},
                            status=200)

    # On error sleep a little against brute force
    sleep(1)

    return eve_response({'success': False, 'token': None, 'token64': None, 'valid': None,
                         'message': 'Wrong username or password'})

@Authenticate.route("/whoami", methods=['GET'])
@Authenticate.route("/self", methods=['GET'])
@require_token()
def get_user():
    """A simple whoami
    Only return 'I am username'"""

    try:
        response, last_modified, etag, status = getitem_internal(resource='users', **{'id': app.globals['id']})

        if status == 200 and '_id' in response:
            return eve_response(data={'iam': response['id']})
    except:
        app.logger.error("Unknown error in get_user")
        return eve_abort(500, 'Unknown error occurred')
"""
@Authenticate.route("/groups", methods=['GET'])
@require_token()
def get_user_groups():
    return eve_response(data=app.globals['acl'])

"""