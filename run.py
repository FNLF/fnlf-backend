"""
    FNLF-backend
    ============

    @todo: Need to implement tests! Eve got it's own tests which can be used, or eve-mocker?
    @todo: CI - via bamboo?
    @todo: Melwin: integration via suds (15 sec+ for licenses...) - make a package/module, see /mw.py
    @todo: Melwin: NEED a query interface for lookups to reduce overhead!!
    @todo: Custom flask routes as blueprints is cleaner, or just as module?
    @todo: Auth & AuthZ - acl lists? Acl groups/roles on user/mackine, corresponding on routes and documents?
    @todo: Application logger setup http://flask.pocoo.org/docs/0.10/errorhandling/ file||database
    @todo: Manual logging facilities see http://flask.pocoo.org/docs/0.10/api/#flask.Flask.logger
            app.logger.debug('A value for debugging')
            app.logger.warning('A warning occurred (%d apples)', 42)
            app.logger.error('An error occurred')
    @todo: Custom eve compatible responses:
            "_issues": {"watchers": "field is read-only", "when": "must be of datetime type"}, 
            "_error": {"code": 422, "message": "Insertion failure: 1 document(s) contain(s) error(s)"}, "_status": "ERR"}


    @note: Pip stuff as a reminder
    
            Update all packages in one go!
            pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip install -U
            
            Find outdated packages
            pip list --outdated
    
    @note: Run as `nohup python run.py >> nlf.log 2>&1&` NB in virtualenv!
    
    @author:  Einar Huseby
    @copyright: (c) 2014 Fallskjermseksjonen Norges Luftsportsforbund
    @license: MIT, see LICENSE for more details. Note that Eve is BSD licensed
"""

__version_info__ = ('0', '2', '0')
__version__ = '.'.join(__version_info__)
__author__ = 'Einar Huseby'
__license__ = 'MIT'
__copyright__ = '(c) 2014 F/NLF'
__all__ = ['fnlf-backend']

import os
from eve import Eve

# We need the json serializer from flask.jsonify (faster than "".json())
# flask.request for custom flask routes (no need for schemas, database or anything else) 
from flask import jsonify, request, abort, Response
import json

# Eve docs (blueprint)
from flask.ext.bootstrap import Bootstrap
from eve_docs import eve_docs

# Import blueprints
from blueprints.authentication import Authenticate
from blueprints.melwin_search import MelwinSearch
from blueprints.observation_workflow import ObsWorkflow
from blueprints.observation_watchers import ObsWatchers
from blueprints.weather import Weather
from blueprints.info import Info
from blueprints.locations import Locations
from blueprints.files import Files
from blueprints.tags import Tags
from blueprints.acl import ACL
from blueprints.observation_share import ObsShare

#import signals from hooks
from ext.signals import signal_activity_log, signal_insert_workflow, \
                      signal_change_owner, signal_init_acl
                      
# Custom url mappings (for flask)
from ext.url_maps import ObjectIDConverter, RegexConverter

# Custom extensions
from ext.tokenauth import TokenAuth

import sys

import arrow

# Debug output use pprint
from pprint import pprint

# Make sure gunicorn passes settings.py
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.py')

# Start Eve (and flask)
# Instantiate with custom auth
app = Eve(auth=TokenAuth, settings=SETTINGS_PATH)
#app = Eve()


""" Define global settings
These settings are mirrored from Eve and should not be
@todo: use app.config instead
"""
app.globals = {"prefix": "/api/v1"}

app.globals.update({"auth": {}})
app.globals['auth'].update({"auth_collection": "users_auth",
                            "users_collection": "users",
                            })

# Start Bootstrap (needed by eve-docs)
Bootstrap(app)

#Custom url mapping (needed by native flask routes)
app.url_map.converters['objectid'] = ObjectIDConverter
app.url_map.converters['regex'] = RegexConverter

# Register eve-docs blueprint 
app.register_blueprint(eve_docs, url_prefix="%s/docs" % app.globals.get('prefix'))

# Register custom blueprints
app.register_blueprint(Authenticate, url_prefix="%s/user" % app.globals.get('prefix'))
app.register_blueprint(MelwinSearch, url_prefix="%s/melwin/users/search" % app.globals.get('prefix'))
app.register_blueprint(Weather, url_prefix="%s/weather" % app.globals.get('prefix'))
app.register_blueprint(Info, url_prefix="%s/info" % app.globals.get('prefix'))
app.register_blueprint(Files, url_prefix="%s/download" % app.globals.get('prefix'))

# Register observation endpoints
app.register_blueprint(ObsWorkflow, url_prefix="%s/observations/workflow" % app.globals.get('prefix'))
app.register_blueprint(ObsWatchers, url_prefix="%s/observations/watchers" % app.globals.get('prefix'))
app.register_blueprint(Locations, url_prefix="%s/locations" % app.globals.get('prefix'))
app.register_blueprint(Tags, url_prefix="%s/tags" % app.globals.get('prefix'))
app.register_blueprint(ACL, url_prefix="%s/users/acl" % app.globals.get('prefix'))
app.register_blueprint(ObsShare, url_prefix="%s/observations/share" % app.globals.get('prefix'))

""" A simple python logger setup
Eve do not yet support logging, but will for 0.5
Use app.logger.<level>(<message>) for manual logging"""
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('log/fnlf-backend.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('FNLF-backend startup')
    
"""

    Eve compatible error message:
    =============================
    
    To be used in custom Flask routes to be compatible with Eve error messages
    
    Should integrate abort/Response
    
    @todo: Use in flask abort
    @todo: Use in flask Response

"""
def eve_error_msg(message, http_code='404'):
    
    return jsonify(**{"_status": "ERR",
                      "_error": {
                                 "message": message,
                                 "code": http_code
                                 }
                      })

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

def observations_before_post(request, payload=None):
    pass

def observations_before_patch(request, lookup):
    
    raise NotImplementedError

def observations_after_patch(request, response):
    """ Change owner, owner is readonly
    """
    signal_change_owner.send(app,response=response)
    
def observations_after_post(request, payload):
    """ When payload as json, request.get_json()
    Else; payload
    @todo: Integrate with ObservationWorkflow!
    @todo: Set expiry as attribute for states!
    """

    signal_insert_workflow.send(app)
    
    signal_init_acl.send(app)
    
    #action, ref, user, resource=None ref, act = None, resource=None, **extra

    pass

def observations_before_get(request, lookup):
    
    raise NotImplementedError
    pass

def users_before_patch(request, response):
    
    #id == id!!
    if app.globals._id != request._id:
        resp = Response(None, 401)
        abort(401, description='You cant edit someone elses account', response=resp)

#app.on_pre_GET_observations += observations_before_get
#app.on_pre_POST_observations += observations_before_post
#app.on_pre_PATCH_observations += observations_before_patch
app.on_post_POST_observations += observations_after_post
#app.on_pre_POST_observations += observations_before_post
app.on_post_PATCH_observations += observations_after_patch
#app.on_pre_PATCH_observations += observations_before_patch

def __anonymize_obs(item):
    """ Anonymizes based on a simple scheme
    Only for after_get_observation
    Should see if solution to have association of user id to a fixed (negative) number for that id to be sorted as "jumper 1", "jumper 2" etc in frontend
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
        
        item['involved'][key]['id'] = -1
        if 'tmpname' in item['involved'][key]:
            item['involved'][key]['tmpname'] = 'Anonymisert'
    
    # Involved in components
    for key, val in enumerate(item['components']):
        
        for k, v in enumerate(item['components'][key]['involved']):
            item['components'][key]['involved'][k]['id'] = -1
    
    # Workflow audit trail        
    for key, val in enumerate(item['workflow']['audit']):
        
        if item['workflow']['audit'][key]['a'] in ['init', 'set_ready', 'send_to_hi', 'withdraw']:
            item['workflow']['audit'][key]['u'] = -1
    
    # Organization        
    for key, val in enumerate(item['organization']):
        
        if 'hl' in item['organization']:    
            for k, hl in enumerate(item['organization']['hl']):
                item['organization']['hl'][k]['id'] = -1
                if 'tmpname' in  item['organization']['hl'][k]:
                    del item['organization']['hl'][k]['tmpname']
        if 'hfl' in item['organization']:          
            for k, hfl in enumerate(item['organization']['hfl']):
                item['organization']['hfl'][k]['id'] = -1
                if 'tmpname' in  item['organization']['hfl'][k]:
                    del item['organization']['hfl'][k]['tmpname']
        if 'hm' in item['organization']:          
            for k, hm in enumerate(item['organization']['hm']):
                item['organization']['hm'][k]['id'] = -1
                if 'tmpname' in item['organization']['hm'][k]:
                    del item['organization']['hm'][k]['tmpname']
        if 'pilot' in item['organization']:          
            for k, pilot in enumerate(item['organization']['pilot']):
                item['organization']['pilot'][k]['id'] = -1
                if 'tmpname' in item['organization']['pilot'][k]:
                    del item['organization']['pilot'][k]['tmpname']
    
    return item

def __has_permission_obs(id, type):
    """ Checks if has type (execute, read, write) permissions on an observation or not
    Only for after_get_observation
    """
    
    col = app.data.driver.db['observations']
    acl = col.find_one({'_id': id}, {'acl': 1})
    
    try:
        if app.globals['acl']['roles'] in acl['acl'][type]['roles'] or app.globals['acl']['groups'] in acl['acl'][type]['groups'] or app.globals['user_id'] in acl['acl'][type]['users']:
            return True
    except:
        return False
    
    return False
    
def after_get_observation(request, response):
    """ Modify response after getting an observation
    """
    
    d = json.loads(response.get_data().decode('UTF-8'))
    
    changed = False
    
    pprint(request.args)
    
    try:
        if '_items' in d:
            
            if request.args.get('version') == 'diffs':
                id = d['_items'][0]['_id']
                if d['_items'][0]['workflow']['state'] == 'closed':
                    for key, val in enumerate(d['_items']):
                        if not __has_permission_obs(id, 'execute'):
                            d['_items'][key] = __anonymize_obs(d['_items'][key])
                            changed = True
            
            else:
                for key, val in enumerate(d['_items']):
                    if d['_items'][key]['workflow']['state'] == 'closed':
                        
                        if not __has_permission_obs(d['_items'][key]['_id'], 'execute'):
                            d['_items'][key] = __anonymize_obs(d['_items'][key])
                            changed = True
                
        else:
            if d['workflow']['state'] == 'closed':
                if not __has_permission_obs(d['_id'], 'execute'):
                    d = __anonymize_obs(d)
                    changed = True
                    
        if changed:
            response.set_data(json.dumps(d))
            
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    
app.on_post_GET_observations += after_get_observation

def before_get_observation(request, lookup):

    lookup.update({ '$or': [{ "acl.read.groups": {'$in': app.globals['acl']['groups']}}, {"acl.read.roles": {'$in': app.globals['acl']['roles']}}, { "acl.read.users": {'$in': [app.globals.get('user_id')]}}] })

app.on_pre_GET_observations += before_get_observation

def before_patch_observation(request, lookup):

    lookup.update({ '$or': [{ "acl.write.groups": {'$in': app.globals['acl']['groups']}}, {"acl.write.roles": {'$in': app.globals['acl']['roles']}}, { "acl.write.users": {'$in': [app.globals.get('user_id')]}}] })

app.on_pre_PATCH_observations += before_patch_observation

def before_post_observation_comments(resource, items):
    items[0].update({'user': int(app.globals.get('user_id'))})
    pprint(items)

app.on_insert += before_post_observation_comments
"""

    START:
    ======
    
    Start the wsgi development server with Eve
    
    Localhost and port 8080
    
    @note: Run development server in background with log as 'nohup python run.py >> nlf.log 2>&1&' 
    @note: Run via gunicorn as 'gunicorn -b localhost:8080 run:app'
    @todo: Config file for gunicorn deployment and -C see http://gunicorn-docs.readthedocs.org/en/latest/settings.html

"""


if __name__ == '__main__':
    port = 8080
    host = '127.0.0.1'

    app.run(host=host, port=port)
