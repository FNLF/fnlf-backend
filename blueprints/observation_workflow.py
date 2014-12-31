"""
    Observation Workflow Controller
    ===============================
    
    Model: workflows.observation class ObservationWorkflow
    
    
    
    simple_page = Blueprint('simple_page', __name__)

class UserAPI(MethodView):

     def get(self):
         users = User.query.all()

     def post(self):
         user = User.from_form_data(request.form)

    simple_page .add_url_rule('/', view_func=UserAPI.as_view('users'))
    
    ===> So this should ALL be contained in the workflow class?? No need to add an extra layer or??
    
    Or rather keep this as a blueprint with the routes being:
    ready
    withdraw
    approve
    reject
    close
    
    Need to have 

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
@ObsWorkflow.route("/<objectid:observation_id>/state", methods=['GET'])
#@require_token()
def state(observation_id):
    
    # No need for user_id, ObservatoinWorkflow already has that!
    wf = ObservationWorkflow(object_id=observation_id, user_id=45199)
    
    return Response(json.dumps(wf.get_current_state()),  mimetype='application/json')

"""
Get audit trail for observation
"""
@ObsWorkflow.route("/<objectid:observation_id>/audit", methods=['GET'])
#@require_token()
def audit(observation_id):
    
    wf = ObservationWorkflow(object_id=observation_id, user_id=45199)
   
    return Response(json.dumps(wf.get_audit(), default=json_util.default), mimetype='application/json')


  
@ObsWorkflow.route("/<objectid:observation_id>/<action>", methods=['GET'])
#@require_token()
def transition(observation_id, action):
    """
    Perform action on observation
    reject, approve, reopen, withdraw
    """
      
    # Instantiate with observation_id and current user (user is from app.globals.user_id
    wf = ObservationWorkflow(object_id=observation_id, user_id=45199)
    
    # Now just do a
    
    if wf.get_resource_mapping().get(action, False):
        
        #result = wf.call(get_actions2().get(action)) #getattr(ObservationWorkflow, wf.get_actions2().get(action))()
        
        # This is actually safe!
        result = eval('wf.' + wf.get_resource_mapping().get(action) + '()')
        print("State triggered: %s" % result)
    
    return Response(json.dumps(wf.state),  mimetype='application/json')

    r = wf.get_current_state()
    
    resp = {'Something': 'Went wrong you jerk'}
    
    # Check if got resource <-> action mapping!
    for v in r.get('actions'):
        if v.get('resource', None) == action:
            #Here we do stuff
            resp = {'Something': 'Yes it was the current blabla '+ seff}
    
    
    print("testing test")
    return Response(json.dumps(resp),  mimetype='application/json')


@ObsWorkflow.route("/<objectid:observation_id>/tasks", methods=['GET'])
#@require_token()
def tasks(observation_id):
    """
    Get tasks for observation
    
    Not implemented yet, should either be integrated in workflow or as a seperate blueprint?
    
    Most likely this will make for another transition where state is 'waiting for tasks to complete'
    """
    wf = ObservationWorkflow(object_id=observation_id, user_id=45199)
   
    return NotImplemented

