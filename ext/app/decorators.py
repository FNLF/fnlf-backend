"""
    Custom decorators
    =================
    
    Custom decorators for various tasks and to bridge Flask with Eve
    
"""
from flask import current_app as app, request, Response, abort
from functools import wraps
import arrow
from datetime import datetime

from ext.auth.tokenauth import TokenAuth
from ext.auth.helpers import Helpers


# Because of circular import in context
try:
    from ext.app.eve_helper import eve_abort
except:

    def eve_abort(status=500, message='', sysinfo=None):
        pass


from threading import Thread


def async(f):
    """ An async decorator
    Will spawn a seperate thread executing whatever call you have
    """
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def track_time_spent(name):
    """Time something
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            start = datetime.now()
            delta = datetime.now() - start
            print(name, "took", delta.total_seconds(), "seconds")
            return f(*args, **kwargs)
        return wrapped
    return decorator   


def require_token():
    """ Custom decorator for token auth
    Wraps the custom TokenAuth class used by Eve and sends it the required param
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            
            auth = TokenAuth()

            try:
                if not auth.check_auth(token=request.authorization['username'], method=request.method, resource=request.path[len(app.globals.get('prefix')):], allowed_roles=None):
                    eve_abort(401, 'Please provide proper credentials')
            except TypeError:
                eve_abort(401, 'No token given, aborting')
            except:
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
    from ext.app.eve_helper import eve_abort
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):

            h = Helpers()
            if int(app.globals['user_id']) not in h.get_superadmins():  # [99999]: # # #
                eve_abort(401, 'You do not have sufficient privileges')

            return f(*args, **kwargs)

        return wrapped

    return decorator
