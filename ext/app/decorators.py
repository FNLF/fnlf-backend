"""
    Custom decorators
    =================
    
    Custom decorators for various tasks and to bridge Flask with Eve
    
"""
from flask import current_app as app, request, Response, abort
from functools import wraps

from ext.auth.tokenauth import TokenAuth
from ext.auth.helpers import Helpers

# Because of circular import in context
from ext.app.eve_helper import eve_abort


class AuthenticationFailed(Exception):
    """Raise custom error"""


class AuthenticationNoToken(Exception):
    """Raise custom error"""


def require_token(allowed_roles=None):
    """ Custom decorator for token auth
    Wraps the custom TokenAuth class used by Eve and sends it the required param
    """

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):

            try:
                # print(request.headers.get('User-Agent'))
                # No authorization in request
                # Let it raise an exception
                try:
                    authorization_token = request.authorization.get('username', None)
                except Exception as e:
                    raise AuthenticationFailed

                # Do the authentication
                # Need to remove prefix + / for request.path
                auth = TokenAuth()
                auth_result = auth.check_auth(token=authorization_token,  # Token
                                              method=request.method,
                                              resource=request.path[len(app.globals.get('prefix')) + 1:],
                                              allowed_roles=allowed_roles)

                if auth_result is not True:
                    raise AuthenticationFailed

            # Catch exceptions and handle correctly
            except AuthenticationFailed:
                eve_abort(401, 'Please provide proper credentials')
            except Exception as e:
                eve_abort(500, 'Server error')

            return f(*args, **kwargs)

        return wrapped

    return decorator


def require_superadmin():
    """Require user to be in a group of hardcoded user id's
    Should use Helpers then get administrators
    @TODO: use a switch for ref [superadmin, admin,..]?
    @TODO: in ext.auth.helpers define a get_users_in_roles_by_ref(ref)?
    """

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            h = Helpers()
            if int(app.globals['user_id']) not in h.get_superadmins():  # [99999]: # # #
                eve_abort(401, 'You do not have sufficient privileges')

            return f(*args, **kwargs)

        return wrapped

    return decorator
