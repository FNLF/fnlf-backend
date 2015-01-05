"""
    Eve Demo
    ========

    Demonstrating an example use of Eve:
    - interfacing existing db from student project
    - all the out of the box features available (filtering, paginating, file upload, etags, versioning, hateos etc etc)
    - autogenerating documentation for resources via eve-docs
    - how to use flask for custom routes, and how to do simple integration with external 3rd party modules
    - how to use events
    - an application structure as a package for seperation
    
    Proposed structure:
    /run.py                - this script, launch with: 'python run-py'
    /settings.py           - required by eve, only global settings imports domains from apps
    /requirements.txt      - should be updated with all modules/packages for easy installing!
    /setup.py              - `python run.py` should setup the entire application
    /ext/*                 - custom library and decorators - extensions
    /blueprints/*          - blueprinted modules
    /apps/*                - directory with all the more or less seperated apps setting files
        /apps/__init__.py         - package file putting it all together
        /apps/auth.py             - the authentication 
        /apps/avviksrapportering.py - avviksrapportering
        /apps/clubs.py            - everything about clubs, admin, authz, locations etc
        /apps/...
    
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
    
    @author:  (c) 2014 by Einar Huseby
    @copyright: (c) 2014 Fallskjermseksjonen Norges Luftsportsforbund
    @license: MIT, see LICENSE for more details. Note that Eve is BSD licensed
"""

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

# Custom url mappings (for flask)
from ext.url_maps import ObjectIDConverter, RegexConverter

# Custom extensions
from ext.tokenauth import TokenAuth

import sys

# Debug output use pprint
from pprint import pprint


# Start Eve (and flask)
# Instantiate with custom auth
app = Eve(auth=TokenAuth)
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
app.register_blueprint(eve_docs, url_prefix="%s/docs" % app.globals['prefix'])

# Register custom blueprints
app.register_blueprint(Authenticate, url_prefix="%s/user" % app.globals['prefix'])
app.register_blueprint(MelwinSearch, url_prefix="%s/melwin/users/search" % app.globals['prefix'])
app.register_blueprint(Weather, url_prefix="%s/weather" % app.globals['prefix'])
app.register_blueprint(Info, url_prefix="%s/info" % app.globals['prefix'])

# Register observation endpoints
app.register_blueprint(ObsWorkflow, url_prefix="%s/observations/workflow" % app.globals['prefix'])
app.register_blueprint(ObsWatchers, url_prefix="%s/observations/watchers" % app.globals['prefix'])


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
    
    Using Eve events
    
    Applies to request and database makes it very extensible
    
    A more advanced use could be to emit a message through a websocket for every defined interaction.
    
    NB: To run a websocket server you need gunicorn or others with support for wsgi.websocket...
    
    @todo: Seperate hooks out 

"""
def pre_persons(request, lookup):
    # Print something
    print("Invoked Pre Get Lookup - on persons!")
    
# Register event
app.on_pre_GET_persons += pre_persons

"""
    Where can user id be added?
    Oplog comes with a auto feature for this
    @todo: Check the manual, verify with auth method choosen
"""
def before_insert_oplog(items):
    
    print(items)
    
app.on_insert_dev += before_insert_oplog

"""
    Let's see what's getting posted!
"""
def pre_avvik(request):
    print(request.data)
    
app.on_pre_POST_avvik += pre_avvik




"""

    START:
    ======
    
    Start the wsgi development server with Eve
    
    Localhost and port 8080
    
    @todo: Use gunicorn

"""
if __name__ == '__main__':
    port = 8080
    host = '127.0.0.1'

    app.run(host=host, port=port)
