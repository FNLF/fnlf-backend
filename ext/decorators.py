"""
    Custom decorators
    =================
    
"""
from flask import current_app as app, request, Response, abort
from functools import wraps
import arrow
import datetime

"""
Time something
"""
def track_time_spent(name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            start = datetime.datetime.now()
            delta = datetime.datetime.now() - start
            print(name, "took", delta.total_seconds(), "seconds")
            return f(*args, **kwargs)
        return wrapped
    return decorator   

"""
Custom decorator wrapping the check_auth functionality and making it accessible to flask.
Not sure how to do this, but this works even if it's ugly bugly!

@note: Needs to be the same as found in ext.tokenauth
"""
def require_token():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            
            try:
                accounts = app.data.driver.db[app.globals['auth']['auth_collection']]
            
                u = accounts.find_one({'auth.token': request.authorization['username']})
    
                if u:
                    utc = arrow.utcnow()
                    if utc.timestamp < arrow.get(u['auth']['valid']).timestamp:
        
                        valid = utc.replace(hours=+1)
                        
                        # If it fails, then token is not renewed
                        accounts.update({'_id': u['_id']}, { "$set": { "auth.valid": valid.datetime } } )
                        
                        app.globals.update({'_id': u['_id']})
                        app.globals.update({'id': u['id']})
                    else:
                        resp = Response(None, 401)
                        abort(401, description='P lease provide proper credentials', response=resp)
                else:
                    resp = Response(None, 401)
                    abort(401, description='P lease provide proper credentials', response=resp)
            
            except:
                resp = Response(None, 401)
                abort(401, description='P lease provide proper credentials', response=resp)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator 