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
from flask import jsonify, request

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

#import signals from hooks
from ext.signals import signal_activity_log, signal_insert_workflow, \
                      signal_change_owner

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
    
    raise NotImplementedError

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
    
    #action, ref, user, resource=None ref, act = None, resource=None, **extra

    pass

def observations_before_get(request, lookup):
    
    raise NotImplementedError
    pass

#app.on_pre_GET_observations += observations_before_get
#app.on_pre_POST_observations += observations_before_post
#app.on_pre_PATCH_observations += observations_before_patch
app.on_post_POST_observations += observations_after_post
app.on_post_PATCH_observations += observations_after_patch
#app.on_pre_PATCH_observations += observations_before_patch

"""
    Where can user id be added?
    Oplog comes with a auto feature for this
    @todo: Check the manual, verify with auth method choosen
"""
def before_insert_oplog(items):
    
    raise NotImplementedError

app.on_insert_oplog += before_insert_oplog


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
