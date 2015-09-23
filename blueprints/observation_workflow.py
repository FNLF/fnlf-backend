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


@ObsWorkflow.route("/<objectid:observation_id>", methods=['GET'])
@ObsWorkflow.route("/<objectid:observation_id>/state", methods=['GET'])
@require_token()
def state(observation_id):
    """ Get current state, actions, transitions and permissions
    """
    # No need for user_id, ObservatoinWorkflow already has that!
    wf = ObservationWorkflow(object_id=observation_id, user_id=app.globals.get('user_id'))
    
    return Response(json.dumps(wf.get_current_state()),  mimetype='application/json')


@ObsWorkflow.route("/<objectid:observation_id>/audit", methods=['GET'])
@require_token()
def audit(observation_id):
    """ Get audit trail for observation
    """    
    wf = ObservationWorkflow(object_id=observation_id, user_id=app.globals.get('user_id'))
   
    return Response(json.dumps(wf.get_audit(), default=json_util.default), mimetype='application/json')

@ObsWorkflow.route("/todo", methods=['GET'])
@require_token()
def get_observations():
    """ Get a number of observations which you can execure
        @todo add max_results from GET
    """
    
    max_results = request.args.get('max_results', 10, type=int)
    page = request.args.get('page', 1, type=int)
    sort_tmp = request.args.get('sort', '_updated', type=str)
    
    sort = {}
    
    if sort_tmp[0] == '-':
        sort['field'] = sort_tmp[1:]
        sort['direction'] = -1
    else:
        sort['field'] = sort_tmp
        sort['direction'] = 1
        
    
    col = app.data.driver.db['observations']
    #db.companies.find().skip(NUMBER_OF_ITEMS * (PAGE_NUMBER - 1)).limit(NUMBER_OF_ITEMS )
    cursor = col.find({'$and': [{'workflow.state': {'$nin': ['closed', 'withdrawn']}}, \
                                {'$or': [{'acl.execute.users': {'$in': [app.globals['user_id']]}}, \
                                {'acl.execute.groups': {'$in': app.globals['acl']['groups']}}, \
                                {'acl.execute.roles': {'$in': app.globals['acl']['roles']}} ] } ] } ).sort(sort['field'], sort['direction'])
    total_items = cursor.count()
    
    _items = list(cursor.skip(max_results * (page - 1)).limit(max_results))
    
    """
    #hateos
    _links = {"self": {"title": "observations/todo", "href": "observations/todo?max_results=%i&page=%i" % (max_results, page), 
                       "next": {},
                       "previous": {},
                       "last": {},
                       "first": {},
                       "parent": {}}}
    """ 
    _meta = { 'page': page,  'max_results' : max_results,  'total' : total_items}   
    result = {'_items' : _items, '_meta':  _meta} 
    return Response(json.dumps(result, default=json_util.default), mimetype='application/json')
  
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

