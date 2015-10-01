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

from datetime import datetime

import json
from bson.objectid import ObjectId

from ext.auth.helpers import helpers
from ext.notifications import notification
    
# TIME & DATE - better with arrow only?
import arrow


_signals = Namespace()

# Define signals
signal_activity_log     = _signals.signal('user-activity-logger')
signal_insert_workflow  = _signals.signal('insert-workflow')
signal_change_owner     = _signals.signal('change-owner')
signal_change_acl       = _signals.signal('change-acl')
signal_init_acl         = _signals.signal('init-acl')

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
         # Notify!
        notify = notification()
        helper = helpers()
        
        recepients = helper.get_melwin_users_email(helper.collect_users(users=[app.globals['user_id']], roles=[helper.get_role_hi(r.get('club'))]))
        subject = 'Observasjon #%s ble opprettet' % number
        
        action_by = helper.get_user_name(app.globals['user_id'])
        
        message = '%s\n' % subject
        message += '\n'
        message += 'Klubb:\t %s\n' % helper.get_melwin_club_name(r.get('club'))
        message += '\n'
        message += 'Av:\t %s\n' % action_by
        message += 'Dato:\t %s\n' % datetime.today().strftime('%Y-%m-%d %H:%M')
        message += 'Url:\t %sapp/obs/#!/observation/%i\n' % (request.url_root, number)
        
        notify.send_email(recepients, subject, message)
        
@signal_init_acl.connect
def init_acl(c_app, **extra):
    """ Set user as read, write and execute!
    Only the current user since this is the POST to DRAFT
    @todo: Investigate wether to keep in workflow or not.
    """
    
    if request.method == 'POST':
    
        r = request.get_json()
        _id = r.get('_id')
        club = r.get('club')
    
        obs = c_app.data.driver.db['observations']
        
        # Add hi to the mix!
        groups = app.data.driver.db['acl_groups']
        group = groups.find_one({'ref': club})
        
        if group:
            roles = app.data.driver.db['acl_roles']
            role = roles.find_one({'group': group['_id'], 'ref': 'hi'})
            
            if role:
                users = app.data.driver.db['users']
                hi = list(users.find({'acl.roles': {'$in': [role['_id']]}}))
                
                his = []
                if isinstance(hi, list):
                    for user in hi:
                        his.append(user['id'])
                else:
                    his.append(hi['id'])
        
        # Adds user and hi!
        acl = {'read': {'users': [app.globals.get('user_id')], 'groups': [], 'roles': [role['_id']]},
               'write': {'users': [app.globals.get('user_id')], 'groups': [], 'roles': []},
               'execute': {'users': [app.globals.get('user_id')], 'groups': [], 'roles': []}
               }
        
        obs.update({'_id': _id}, {'$set': {'acl': acl}})
        obs.update({'_id': _id}, {'$set': {'organization.hi': his}})
        
    

@signal_change_owner.connect
def change_owner(c_app, response, **extra):
    """ This solution hooks into after a PATCH request and thus needs the response obj
    The trick is to take the body returned via .get_data() and load it as json
    This ONLY works for Eve specific calls if you do not return the _id included in a json string
    """

    r = json.loads(response.get_data().decode())
    _id = r.get('_id') #ObjectId(r['_id'])
    
    try:
        observation = c_app.data.driver.db['observations']
        u = observation.update({'_id': ObjectId(_id)}, 
                               { "$set": {"owner": c_app.globals.get('user_id') }
                                })
    except:
        pass

@signal_change_acl.connect
def change_obs_acl(c_app, acl, **extra):
    
    #observation = c_app.data.driver.db['observations']
    #u = observation.update({})
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
    

    




    
    