"""
    Custom decorators
    =================
    
"""
from flask import current_app as app, request, Response, abort
from functools import wraps
import arrow
from datetime import datetime

from ext.tokenauth import TokenAuth

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
            
            if not auth.check_auth(token=request.authorization['username'], 
                                   method=request.method, 
                                   resource=request.path[len(app.globals.get('prefix')):], 
                                   allowed_roles=None):
                
                resp = Response(None, 401)
                abort(401, description='Please provide proper credentials', response=resp)
                
            return f(*args, **kwargs)
        return wrapped
    return decorator 