"""
	Decorators without response
	===========================
	
	NO response object should be used or

"""
from functools import wraps
from threading import Thread
from datetime import datetime

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