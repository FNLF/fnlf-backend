"""
    Watchers
    ========
    
    Simple watchers resource
    
    - Show who's watching
    - Add and remove yourself
    - Automatic watching??
    - Signals - start/stop watching
    - audit?
    
    See signals on http://stackoverflow.com/questions/16163139/catch-signals-in-flask-blueprint
    
    
"""

from flask import Blueprint, current_app as app, request, Response, abort, jsonify
from bson import json_util
import json
import re

# Need custom decorators
from ext.decorators import *



ObsWatchers = Blueprint('Observation Watchers', __name__,)

@ObsWatchers.route("/<objectid:observation_id>/", methods=['GET'])
@ObsWatchers.route("/<objectid:observation_id>/watchers", methods=['GET'])
#@require_token()
def watchers(observation_id):
    
    w = get_watchers(observation_id)
    
    return jsonify(**{'watchers': w})

@ObsWatchers.route("/<objectid:observation_id>/watching", methods=['GET'])
@require_token()
def is_watching(observation_id):
    
    # if app.user_id in watchers()
    #    return True
    from pprint import pprint
    print("USER GLOBALS")
    pprint(app.globals)
    
    if app.globals.get('user_id') in get_watchers(observation_id):
        return jsonify(**{'watching': True})
    
    return jsonify(**{'watching': False})

@ObsWatchers.route("/<objectid:observation_id>/start", methods=['GET'])
#@require_token()
def start(observation_id):
    
    # Patch internal
    
    return NotImplemented

@ObsWatchers.route("/<objectid:observation_id>/stop", methods=['GET'])
#@require_token()
def stop(observation_id):
    
    # Patch internal
    
    return NotImplemented

def get_watchers(observation_id):
    
    col = app.data.driver.db['observations']
    
    r = col.find_one({'_id': observation_id}, {'watchers': 1})
   
    return r['watchers']
    
    

