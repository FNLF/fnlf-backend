"""
    Signal connections
    ==================
    
    @todo: Need to make functions generic, ie parse resource/endpoint dynamically \
           or via mappings
    
"""


from flask import current_app as app, request, Response, abort

from flask.signals import Namespace

from eve.methods.post import post_internal
from eve.methods.common import oplog_push

# TIME & DATE - better with arrow only?
import arrow


_signals = Namespace()

# Define signals
signal_activity_log     = _signals.signal('user-activity-logger')
signal_insert_workflow  = _signals.signal('insert-workflow')
signal_change_owner     = _signals.signal('change-owner')

@signal_insert_workflow.connect
def insert_workflow(c_app, **extra):
    """ Inserts workflow, wathcers, owner, reporter and custom id on the current resource
    Only when method equals POST
    @todo: need resource->workflow mapping
    @todo: should hook into the given workflow (from mapping?)and retrieve schema OR schema is fixed
    @todo: generic means it can find what to do for each resource (mappings?)
    """
    
    if request.method == 'POST':
    
        r = request.get_json()
        _id = r.get('_id')
        _etag = r.get('_etag')
        _version = r.get('_version')
        utc = arrow.utcnow()
        
        workflow = {"name": "ObservationWorkflow",
                    "comment": "Initialized workflow",
                    "state": "draft",
                    "last_transition": utc.datetime,
                    "expires":  utc.replace(days=+7).datetime,
                    "audit" : [{'a': "init",
                               'r': "init",
                               'u': c_app.globals.get('user_id'),
                               's': None,
                               'd': "draft",
                               'v': _version,
                               't': utc.datetime,
                               'c': "Initialized workflow" } ]
                    }
        
        watchers = [c_app.globals.get('user_id')]
        
        # Make a integer increment from seq collection
        seq = c_app.data.driver.db['seq']
        seq.update({'c': 'observations'}, {'$inc': {'i': int(1)}}, True) #,fields={'i': 1, '_id': 0},new=True).get('i')
        seq_r = seq.find_one({'c': 'observations'}, {'i': 1, '_id': 0})
        number = int(seq_r.get('i'))
        
        observation = c_app.data.driver.db['observations']
        observation.update({'_id': _id, '_etag': _etag}, 
                           { "$set": {"workflow": workflow,
                                      "id": number,
                                      "watchers": watchers, 
                                      "owner": c_app.globals.get('user_id'),
                                      "reporter": c_app.globals.get('user_id')
                                      } 
                            })
        
@signal_change_owner.connect
def change_owner(c_app, response, **extra):
    """ This solution hooks into after a PATCH request and thus needs the response obj
    The trick is to take the body returned via .get_data() and load it as json
    This ONLY works for Eve specific calls if you do not return the _id included in a json string
    """
    import json
    from bson.objectid import ObjectId
    r = json.loads(response.get_data().decode())
    _id = r.get('_id') #ObjectId(r['_id'])
    
    try:
        observation = c_app.data.driver.db['observations']
        u = observation.update({'_id': ObjectId(_id)}, 
                               { "$set": {"owner": c_app.globals.get('user_id') }
                                })
    except:
        pass

@signal_activity_log.connect
def oplog_wrapper( c_app, ref=None, updates=None, action=None, resource=None, **extra):
    """ A simple activity logger wrapping eve's push_oplog
    @todo: Testing and validating of the oplog_push from eve
    @todo: Implement workflow, watchers etc as op (operations)
    """
    
    raise NotImplementedError
    
    #def oplog_push(resource, updates, op, id=None):
    
    if ref == None:
        if request.method == 'POST': #We do not have any ref before returning, should be sendt!
            pass
        else:
            r = request.get_json() #Got all _id and _etag
            ref = r.get('_id')
    
    """ request.endpoint
    A string with 'endpoint|resource' syntax
    """
    if resource == None:
        if request.endpoint:
            resource = request.endpoint.split('|')[0]
        else: 
            resource = 'Unknown'
            
    """ This is NOT tested yet
    @todo: need to replicate the updates dict, which is payload (r?)
    """
    oplog_push(resource=resource, updates=r, op=request.method, id=ref)
    

    




    
    