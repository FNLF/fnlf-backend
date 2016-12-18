"""
    ACL
    ===
    
    Custom wrapper for acl's!
    
    
"""

from flask import Blueprint, current_app as app, request, Response, abort, jsonify
from bson import json_util
import json

# from eve.methods.patch import patch_internal

from bson.objectid import ObjectId
# Need custom decorators
from ext.app.decorators import *

import ext.auth.acl as acl_helper
from ext.app.eve_helper import eve_abort, eve_response

ACL = Blueprint('Acl', __name__, )


@ACL.route("/<string:collection>/<int:observation_id>", methods=['GET'])
@require_token()
@require_superadmin()
def get_observation_user_acl(collection, observation_id):
    ''' This is NOT a good one since jsonifying those objectid's are bad
    Should rather use Eve for getting stuff!
    '''

    result = acl_helper.get_user_permissions(observation_id, collection)

    return eve_response(result)


@ACL.route("/group/<objectid:group_id>", methods=['GET'])
@require_token()
@require_superadmin()
def get_users_by_group(group_id):

    col = app.data.driver.db['users']
    r = col.find({'acl.groups': {'$in': [group_id]}})

    return eve_response({'users': r})  # jsonify(**{'users': r})


@ACL.route("/<int:username>", methods=['GET'])
@require_token()
@require_superadmin()
def get_user_acl(username):
    ''' This is NOT a good one since jsonifying those objectid's are bad
    Should rather use Eve for getting stuff!
    '''

    col = app.data.driver.db['users']
    r = col.find_one({'id': username}, {'acl': 1, 'id': 1})
    r['_id'] = str(r['_id'])
    return eve_response(r)


@ACL.route("/<int:username>/group/<objectid:groupid>", methods=['POST'])
@require_token()
@require_superadmin()
def add_group_acl(username, groupid):
    col = app.data.driver.db['users']

    r = col.update({'id': username}, {"$addToSet": {"acl.groups": ObjectId(groupid)}})

    return eve_response(r)


@ACL.route("/<int:username>/role/<objectid:roleid>", methods=['POST'])
@require_token()
@require_superadmin()
def add_role_acl(username, roleid):
    col = app.data.driver.db['users']

    r = col.update({'id': username}, {"$addToSet": {"acl.roles": ObjectId(roleid)}})

    return eve_response(r)


@ACL.route("/<int:username>/group/<objectid:groupid>", methods=['DELETE'])
@require_token()
@require_superadmin()
def delete_group_acl(username, groupid):
    col = app.data.driver.db['users']

    r = col.update({'id': username}, {"$pull": {"acl.groups": ObjectId(groupid)}})

    return eve_response(r)


@ACL.route("/<int:username>/role/<objectid:roleid>", methods=['DELETE'])
@require_token()
@require_superadmin()
def delete_role_acl(username, roleid):
    col = app.data.driver.db['users']

    r = col.update({'id': username}, {"$pull": {"acl.roles": ObjectId(roleid)}})

    return eve_response(r)


@ACL.route("/hi/<club>", methods=['GET'])
@require_token()
@require_superadmin()
def get_club_hi(club):
    groups = app.data.driver.db['acl_groups']
    group = groups.find_one({'ref': club})

    if group:
        roles = app.data.driver.db['acl_roles']
        role = roles.find_one({'group': group['_id'], 'ref': 'hi'})

        if role:
            users = app.data.driver.db['users']
            hi = list(users.find({'acl.roles': {'$in': [role['_id']]}}))

            r = []
            if isinstance(hi, list):

                for user in hi:
                    r.append(user['id'])
            else:
                r.append(hi['id'])

                return eve_response(r)

    eve_abort(501, 'Unknown error occurred')
