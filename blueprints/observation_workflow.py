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


  
@ObsWorkflow.route('/<objectid:observation_id>/<regex("(approve|reject|withdraw|reopen)"):action>', methods=['POST'])
@require_token()
def transition(observation_id, action):
    """
    Perform action on observation
    reject, approve, reopen, withdraw
    request.form.get 
    request.args.get ?q=tal
    @todo: include comment in post!
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
       
    return Response(json.dumps(wf.state),  mimetype='application/json')

    """
    @todo: For removal:
    r = wf.get_current_state()
    
    resp = {'Something': 'Went wrong'}
    
    # Check if got resource <-> action mapping!
    for v in r.get('actions'):
        if v.get('resource', None) == action:
            #Here we do stuff
            resp = {'Something': 'Yes it was the current blabla '+ seff}
    
    
    print("testing test")
    return Response(json.dumps(resp),  mimetype='application/json')
    """

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

