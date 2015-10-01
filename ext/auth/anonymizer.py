from flask import current_app as app
from bson.objectid import ObjectId
import ext.auth.acl as acl_helper

def anonymize_obs(item):
    """ Anonymizes based on a simple scheme
    Only for after_get_observation
    Should see if solution to have association of user id to a fixed (negative) number for that id to be sorted as "jumper 1", "jumper 2" etc in frontend
    @todo: remove anon files from list 
    @todo: add check for nanon's (non-anon) which should return item directly
    @todo: see if you are involved then do not anon that?
    @todo: for workflow see if all involved should be added to nanon or seperate logic to handle that?
    @todo: add "hopper 1" "hopper 2" etc involved[45199] = -3
    """
    
    # Reporter AND owner
    item['reporter'] = -1
    item['owner'] = -1
    
    if 'audit' not in item['workflow']:
        item['workflow']['audit'] = []
        
    if 'involved' not in item:
        item['involved'] = []
    
    if 'components' not in item:
        item['components'] = []
    
    # Involved
    for key, val in enumerate(item['involved']):
        
        try:
            item['involved'][key]['id'] = -1
            if 'tmpname' in item['involved'][key]:
                item['involved'][key]['tmpname'] = 'Anonymisert'
        except KeyError:
            pass
        except:
            print("Unexpected error:", sys.exc_info()[0])
            pass
    
    # Involved in components
    for key, val in enumerate(item['components']):
        try:
            for k, v in enumerate(item['components'][key]['involved']):
                
                if 'tmpname' in item['components'][key]['involved'][k]:
                    del item['components'][key]['involved'][k]['tmpname']
                    item['components'][key]['involved'][k]['id'] = -1
                    
                elif 'id' in item['components'][key]['involved'][k]:
                    item['components'][key]['involved'][k]['id'] = -1
                
        except KeyError:
            pass
        except:
            print("Unexpected error:", sys.exc_info()[0])
            pass
    
    # Files
    item['files'][:] = [d for d in item['files'] if d.get('r') != True]
    
    # Workflow audit trail        
    for key, val in enumerate(item['workflow']['audit']):
        
        try:
            if item['workflow']['audit'][key]['a'] in ['init', 'set_ready', 'send_to_hi', 'withdraw']:
                item['workflow']['audit'][key]['u'] = -1
        except KeyError:
            pass
        except:
            print("Unexpected error:", sys.exc_info()[0])
            pass
    
    # Organization        
    for key, val in enumerate(item['organization']):
        
        try:
            if 'hl' in item['organization']:    
                for k, hl in enumerate(item['organization']['hl']):
                    if 'id' in item['organization']['hl'][k]:
                        item['organization']['hl'][k]['id'] = -1
                    if 'tmpname' in  item['organization']['hl'][k]:
                        del item['organization']['hl'][k]['tmpname']
            if 'hfl' in item['organization']:          
                for k, hfl in enumerate(item['organization']['hfl']):
                    if 'id' in item['organization']['hfl'][k]:
                        item['organization']['hfl'][k]['id'] = -1
                    if 'tmpname' in  item['organization']['hfl'][k]:
                        del item['organization']['hfl'][k]['tmpname']
            if 'hm' in item['organization']:          
                for k, hm in enumerate(item['organization']['hm']):
                    if 'id' in item['organization']['hm'][k]:
                        item['organization']['hm'][k]['id'] = -1
                    if 'tmpname' in item['organization']['hm'][k]:
                        del item['organization']['hm'][k]['tmpname']
            if 'pilot' in item['organization']:          
                for k, pilot in enumerate(item['organization']['pilot']):
                    if 'id' in item['organization']['pilot'][k]:
                        item['organization']['pilot'][k]['id'] = -1
                    if 'tmpname' in item['organization']['pilot'][k]:
                        del item['organization']['pilot'][k]['tmpname']
        except KeyError:
            pass
        except:
            print("Unexpected error:", sys.exc_info()[0])
            pass
        
    return item

def has_permission_obs(id, type):
    """ Checks if has type (execute, read, write) permissions on an observation or not
    Only for after_get_observation
    @note: checks on list comprehension and returns number of intersects in list => len(list) > 0 == True
    @bug: Possible bug if user comparison is int vs float!
    @todo: Should not be execute rights? Or could it be another type 'noanon' or if in users with read right? 
    """
    
    return acl_helper.has_permission(ObjectId(id), type, 'observations')
    
    return False