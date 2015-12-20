"""

    ACL functions
    =============
    
    @see: blueprints/acl.py for use
    
    @todo: Make this more solid!
    @todo: Handle id and _id gracefully
"""

from flask import current_app as app
from bson.objectid import ObjectId

def has_permission(id, type, collection):
    """ Checks if current user has type (execute, read, write) permissions on an collection or not
    @note: checks on list comprehension and returns number of intersects in list => len(list) > 0 == True
    @bug: Possible bug if user comparison is int vs float!
    """
    
    col = app.data.driver.db[collection]
    
    # We can find by id and _id
    try:
        o = ObjectId(id)
        if o == ObjectId(str(o)):
            acl = col.find_one({'_id': ObjectId(id)}, {'acl': 1})
        else:
            acl = col.find_one({'id': id}, {'acl': 1})
    
    except:
        acl = col.find_one({'id': id}, {'acl': 1})
        pass
    
    acl = col.find_one({'_id': ObjectId(id)}, {'acl': 1})
    try:
        if len([i for i in app.globals['acl']['roles'] if i in acl['acl'][type]['roles']]) > 0 \
        or len([i for i in app.globals['acl']['groups'] if i in acl['acl'][type]['groups']]) > 0 \
        or app.globals['user_id'] in acl['acl'][type]['users']:
            return True
    except:
        return False
    
    return False

def get_user_permissions(id, collection):
    
    try:
        if collection not in ['observations', 'users']:
            collection = 'observations'
        
        x = False
        w = False
        r = False
        
        col = app.data.driver.db[collection]
        
        try:
            o = ObjectId(id)
            if o == ObjectId(str(o)):
                acl = col.find_one({'_id': ObjectId(id)}, {'acl': 1, 'id': 1, '_id': 1})
            else:
                acl = col.find_one({'id': id}, {'acl': 1, 'id': 1, '_id': 1})
    
        except:
            acl = col.find_one({'id': id}, {'acl': 1, 'id': 1, '_id': 1})
            pass
    
        
        try:
            if len([i for i in app.globals['acl']['roles'] if i in acl['acl']['execute']['roles']]) > 0 \
            or len([i for i in app.globals['acl']['groups'] if i in acl['acl']['execute']['groups']]) > 0 \
            or app.globals['user_id'] in acl['acl']['execute']['users']:
                x = True
        except:
            pass
        
        try:
            if len([i for i in app.globals['acl']['roles'] if i in acl['acl']['read']['roles']]) > 0 \
            or len([i for i in app.globals['acl']['groups'] if i in acl['acl']['read']['groups']]) > 0 \
            or app.globals['user_id'] in acl['acl']['read']['users']:
                r = True
        except:
            pass
        
        try:
            if len([i for i in app.globals['acl']['roles'] if i in acl['acl']['write']['roles']]) > 0 \
            or len([i for i in app.globals['acl']['groups'] if i in acl['acl']['write']['groups']]) > 0 \
            or app.globals['user_id'] in acl['acl']['write']['users']:
                w = True
        except:
            pass
        
        return {'id': acl['id'],'_id': acl['_id'], 'resource': collection, 'u': app.globals['user_id'], 'r': r, 'w': w, 'x': x}
        
    except:
        return {'_error': {'code': 404, 'message': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.' },\
                '_status': 'ERR'}
        
        
    return result


    
    
