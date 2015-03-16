"""
    Observation Workflow Controller
    ===============================
    
    Model: workflows.observation.ObservationWorkflow
    
    @todo: Signals on change signal to communications to dispatch an update to the watchers
           http://stackoverflow.com/questions/16163139/catch-signals-in-flask-blueprint

"""

from flask import Blueprint, current_app as app, request, Response, abort, jsonify
from bson import json_util
import json
import re

from workflows.observation import ObservationWorkflow

# Need custom decorators
from ext.decorators import *


ObsWorkflow = Blueprint('Observation Workflow', __name__,)

"""
Get current state, actions, transitions and permissions
"""
@ObsWorkflow.route("/<objectid:observation_id>", methods=['GET'])
@ObsWorkflow.route("/<objectid:observation_id>/state", methods=['GET'])
@require_token()
def state(observation_id):
    
    # No need for user_id, ObservatoinWorkflow already has that!
    wf = ObservationWorkflow(object_id=observation_id, user_id=app.globals.get('user_id'))
    
    return Response(json.dumps(wf.get_current_state()),  mimetype='application/json')

"""
Get audit trail for observation
"""
@ObsWorkflow.route("/<objectid:observation_id>/audit", methods=['GET'])
@require_token()
def audit(observation_id):
    
    wf = ObservationWorkflow(object_id=observation_id, user_id=app.globals.get('user_id'))
   
    return Response(json.dumps(wf.get_audit(), default=json_util.default), mimetype='application/json')

@ObsWorkflow.route("/todo", methods=['GET'])
@require_token()
def get_observations():
    
    col = app.data.driver.db['observations']
    
    r = list(col.find({'$and': [{'workflow.state': {'$nin': ['closed', 'withdrawn']}}, \
                                {'$or': [{'acl.execute.users': {'$in': [app.globals['user_id']]}}, \
                                {'acl.execute.groups': {'$in': app.globals['acl']['groups']}}, \
                                {'acl.execute.roles': {'$in': app.globals['acl']['roles']}} ] } ] } ).sort('_updated', 1))
    return Response(json.dumps({'_items': r}, default=json_util.default), mimetype='application/json')
  
@ObsWorkflow.route('/<objectid:observation_id>/<regex("(approve|reject|withdraw|reopen)"):action>', methods=['POST'])
@require_token()
def transition(observation_id, action):
    """
    Perform action on observation
    reject, approve, reopen, withdraw
    request.form.get 
    request.args.get ?q=tal
    @todo: include comment in post!
    @todo: check permissions here??
    """
    
    comment = None
    try:
        args = request.get_json() #use force=True to do anyway!
        comment = args.get('comment')
    except:
        # Could try form etc
        pass
    
    # Instantiate with observation_id and current user (user is from app.globals.user_id
    wf = ObservationWorkflow(object_id=observation_id, user_id=app.globals.get('user_id'), comment=comment)
    
    # Now just do a
    
    if wf.get_resource_mapping().get(action, False):
        
        #result = wf.call(get_actions2().get(action)) #getattr(ObservationWorkflow, wf.get_actions2().get(action))()
        
        # This is actually safe!
        result = eval('wf.' + wf.get_resource_mapping().get(action) + '()')
        
        # Change owner signal
        #signal_change_owner.send(app,response=response)
       
    return Response(json.dumps(wf.state),  mimetype='application/json')


@ObsWorkflow.route("/<objectid:observation_id>/tasks", methods=['GET'])
@require_token()
def tasks(observation_id):
    """
    Get tasks for observation
    
    Not implemented yet, should either be integrated in workflow or as a seperate blueprint?
    
    Most likely this will make for another transition where state is 'waiting for tasks to complete'
    """
    #wf = ObservationWorkflow(object_id=observation_id, user_id=app.globals.get('user_id'))
   
    raise NotImplemented

