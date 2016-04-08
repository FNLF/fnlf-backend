
from flask import request, Response, abort, jsonify

import threading
import sys
from eve.methods.post import post_internal
from eve.methods.patch import patch_internal
from eve.methods.get import getitem as get_internal

from ext.app.decorators import async, track_time_spent
import datetime, time

from .melwin import Melwin

@async
@track_time_spent('Melwin Update')
def do_melwin_update(app):

    m = Melwin()

    persons = m.get_all()
    print("Finished get all in dummy")
    for key, user in persons.items():
        print("Starting loop fopr persons")
        
        """
        Try get on id (alternative lookup)
        
        if 200:
        patch
        
        if 404:
        post
        """
        
        #print('PERSON')
        #pprint(person)
        lookup = {"id": user['id']}
        user.pop("id", None)
        #def patch_internal(resource, payload=None, concurrency_check=False,skip_validation=False, **lookup):
        
        #Need correct context or fails miserable!
        with app.test_request_context("/%s/%s/melwin/users" % (app.config.get('URL_PREFIX'), app.config.get('API_VERSION'))):
            try:
                r, _, _, status = patch_internal('melwin/users', user, False, True, **lookup)
                print("[PATCH INTERNAL]")
            except:
                user.update(lookup)
                try:
                    r, _, _, status = post_internal(resource='melwin/users', payl=user, skip_validation=True)
                except:
                    print("ERROR")
                print("[POST INTERNAL]")
                
                """
                status['_status'] == 'OK'
                _id
                """
            
            print(r)
            print(status)
    
        
        #Run every:
        #Should rather have a now + at least 24 hours, then at 04:00...
        #Or last updated?
        #seconds = get_timer() + 1000000
        #threading.Timer(seconds,do_melwin_update, [app]).start()


def get_timer():
    """Return seconds until we run
    """
    #Tomorrows date + time!
    tomorrow = datetime.datetime.combine((datetime.date.today() + datetime.timedelta(days=0)), datetime.time(18, 0))
    #Unix timestamp, just find seconds
    seconds = int(time.mktime(tomorrow.timetuple()) - time.time())
    
    
    return seconds
           
def start(app):
    """Schedule after startup for first run
    @todo: smart schedule "04 tomorrow"
    """
    
    s = get_timer()
    print(s)
    
    threading.Timer(get_timer(),do_melwin_update, [app]).start()
    
    
    
