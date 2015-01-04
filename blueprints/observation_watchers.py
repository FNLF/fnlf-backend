"""
    Watchers
    ========
    
    Simple watchers resource
    
    - start and stop watching
    - 
    
    @todo: add signals on start and stop for audit
    @todo: implement updating from workflow?
    @todo: refactor and have all changes in a model, this being the controller hence it can be called from other resources
    
    See signals on http://stackoverflow.com/questions/16163139/catch-signals-in-flask-blueprint
    
    
"""

from flask import Blueprint, current_app as app, request, Response, abort, jsonify
from bson import json_util
import json

from eve.methods.patch import patch_internal

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
    
    if app.globals.get('user_id') in get_watchers(observation_id):
        return jsonify(**{'watching': True})
    
    return jsonify(**{'watching': False})

@ObsWatchers.route("/<objectid:observation_id>/start", methods=['GET'])
@require_token()
def start(observation_id):
    """ Start watching an observation """
    
    w = get_watchers(observation_id)
    
    if app.globals.get('user_id') not in w:
        new_watchers = []
        new_watchers.append(app.globals.get('user_id'))
        new_watchers.extend(w)
        
        r = update_watchers(observation_id, new_watchers)
        
        if r:
            return jsonify(**{'watching': True})
    
    return jsonify(**{'watching': False})

@ObsWatchers.route("/<objectid:observation_id>/stop", methods=['GET'])
@require_token()
def stop(observation_id):
    
    w = get_watchers(observation_id)
    
    if app.globals.get('user_id') in w:

        w = [x for x in w if x != app.globals.get('user_id')]

        r = update_watchers(observation_id, w)
        
        if r:
            return jsonify(**{'watching': False})
    
    return jsonify(**{'watching': True})

def get_watchers(observation_id):
    
    col = app.data.driver.db['observations']
    
    r = col.find_one({'_id': observation_id}, {'watchers': 1})
   
    return r['watchers']

def update_watchers(observation_id, watchers):
    """ Wrapper to keep update segregated """
    
    col = app.data.driver.db['observations']

    r = col.update({'_id': observation_id}, {"$set": {"watchers": watchers}})
    
    if r:
        return True
    
    return False
    
    

