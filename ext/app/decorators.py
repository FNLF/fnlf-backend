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



def require_token():
    """ Custom decorator for token auth
    Wraps the custom TokenAuth class used by Eve and sends it the required param
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):

            auth = TokenAuth()
            auth.check_auth(token=request.authorization['username'], method=request.method,
                            resource=request.path[len(app.globals.get('prefix')):], allowed_roles=None)
            try:
                if not auth.check_auth(token=request.authorization['username'], method=request.method, resource=request.path[len(app.globals.get('prefix')):], allowed_roles=None):
                    eve_abort(401, 'Please provide proper credentials')
                    app.logger.info("Did not aauthenticate")
            except TypeError:
                app.logger.exception("Did not aauthenticate")
                eve_abort(401, 'No token given, aborting')
            except:
                app.logger.exception("Did not aauthenticate we dont know")
                eve_abort(500, "Whats going on? We don't know.")

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
