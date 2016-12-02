
"""

    Event hooks:
    ============
    
    Using Eve defined events 
    
    Mixed with signals to ext.hooks for flask and direct database access compatibility
    
    Eve specific hooks are defined according to
    
    def <resource>_<when>_<method>():
    
    When attaching to app, remember to use post and pre for request hooks
           
    @note: all requests are supported: GET, POST, PATCH, PUT, DELETE
    @note: POST (resource, request, payload)
    @note: POST_resource (request, payload)
    @note: GET (resource, request, lookup)
    @note: GET_resource (request, lookup)

"""
from flask import current_app as app
import ext.auth.anonymizer as anon
import json
import sys

#import signals from hooks
from ext.hooks.signals import signal_activity_log, signal_insert_workflow, \
                      signal_change_owner, signal_init_acl

def before_post(request, payload=None):
    pass

def before_patch(request, lookup):
    
    raise NotImplementedError

def after_patch(request, response):
    """ Change owner, owner is readonly
    """
    signal_change_owner.send(app,response=response)
    
def after_post(request, payload):
    """ When payload as json, request.get_json()
    Else; payload
    @todo: Integrate with ObservationWorkflow!
    @todo: Set expiry as attribute for states!
    """

    signal_insert_workflow.send(app)
    
    signal_init_acl.send(app)
    
    #action, ref, user, resource=None ref, act = None, resource=None, **extra

    pass

def before_get(request, lookup):
    
    raise NotImplementedError
    pass

        
def after_get(request, response):
    """ Modify response after GETing an observation
    """
    
    d = json.loads(response.get_data().decode('UTF-8'))
    
    # Just to be sure, we remove all data if anything goes wrong!
    #response.set_data({})

    changed = False
    
    try:
        if '_items' in d:
            
            if request.args.get('version') == 'diffs':
                id = d['_items'][0]['_id']
                if d['_items'][0]['workflow']['state'] == 'closed':
                    for key, val in enumerate(d['_items']):
                        if not anon.has_permission_obs(id, 'execute'):
                            d['_items'][key] = anon.anonymize_obs(d['_items'][key])
                            changed = True
            
            else:
                for key, val in enumerate(d['_items']):
                    if d['_items'][key]['workflow']['state'] == 'closed':
                        
                        if not anon.has_permission_obs(d['_items'][key]['_id'], 'execute'):
                            d['_items'][key] = anon.anonymize_obs(d['_items'][key])
                            changed = True
                
        else:
            if d['workflow'] and 'state' in d['workflow']:
                if d['workflow']['state'] == 'closed':
                    if not anon.has_permission_obs(d['_id'], 'execute'):
                        d = anon.anonymize_obs(d)
                        changed = True
                    
        if changed:
            response.set_data(json.dumps(d))
            changed = False
    except KeyError:
        app.logger.info("Keyerror in hook")
        pass        
    except:
        app.logger.info("Unexpected error: ", sys.exc_info()[0])
    


def before_get(request, lookup):

    lookup.update({ '$or': [{ "acl.read.groups": {'$in': app.globals['acl']['groups']}}, \
                            {"acl.read.roles": {'$in': app.globals['acl']['roles']}}, \
                            { "acl.read.users": {'$in': [app.globals.get('user_id')]}}] })



def before_patch(request, lookup):

    lookup.update({ '$or': [{ "acl.write.groups": {'$in': app.globals['acl']['groups']}}, \
                            {"acl.write.roles": {'$in': app.globals['acl']['roles']}}, \
                            { "acl.write.users": {'$in': [app.globals.get('user_id')]}}] })



def before_post_comments(resource, items):
    print(resource)
    if resource == 'observation/comments':
        items[0].update({'user': int(app.globals.get('user_id'))})
        
