
from flask import current_app as app
import ext.app.eve_helper as eve_helper
import ext.auth.helpers as h
import json
from bson.objectid import ObjectId

helper = h.Helpers()

def before_post(request, payload=None):

    print(request)
    print(payload)

    superadmin = helper.get_role_by_ref(ref='superadmin')

    if superadmin in app.globals['acl']['roles']:
        payload['owner'] = app.globals['user_id']

    else:
        eve_helper.eve_abort(404, 'No access to this item')

def after_post(request, response):

    try:
        payload = json.loads(response.get_data().decode('UTF-8'))
        print(payload)
    except:
        print('Error')
    if request.method == 'POST' and '_id' in payload and payload['_status'] == 'OK':
        superadmin = helper.get_role_by_ref(ref='superadmin')
        acl = {'write': {'roles': [superadmin]}}
        col = app.data.driver.db['help']
        col.update_one({'_id': ObjectId(payload.get('_id'))}, {"$set": {"acl": acl}})


def before_patch(request, lookup):
    print(request)
    print(lookup)
    lookup.update({'$or': [{"acl.write.groups": {'$in': app.globals['acl']['groups']}},
                           {"acl.write.roles": {'$in': app.globals['acl']['roles']}},
                           {"acl.write.users": {'$in': [app.globals.get('user_id')]}}]})


def before_delete(request, lookup):
    lookup.update({'$or': [{"acl.write.groups": {'$in': app.globals['acl']['groups']}},
                           {"acl.write.roles": {'$in': app.globals['acl']['roles']}},
                           {"acl.write.users": {'$in': [app.globals.get('user_id')]}}]})