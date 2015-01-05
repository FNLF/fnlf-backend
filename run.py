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
    
    @author:  Einar Huseby
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

import arrow

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
    
    @todo: How to run in seperate file
    
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
    """ Need to get data from response
    """
    import json
    from bson.objectid import ObjectId
    
    r = json.loads(response.get_data().decode())
    pprint(r.get('_id'))
    _id = r.get('_id') #ObjectId(r['_id'])
    pprint(ObjectId(_id))
    
    try:
        observation = app.data.driver.db['observations']
        u = observation.update({'_id': ObjectId(_id)}, 
                               { "$set": {"owner": app.globals.get('user_id')} 
                                })
        pprint(u)
    except:
        print("SOMTHING AWFUL HAPPENED")
        pprint(u)
        
    
    pass

def observations_after_post(request, payload):
    """ When payload as json, request.get_json()
    Else; payload
    @todo: Integrate with ObservationWorkflow!
    @todo: Set expiry as attribute for states!
    """
    r = request.get_json() #Got all _id and _etag
    
    _id = r.get('_id')
    _etag = r.get('_etag')
    _version = r.get('_version')
    utc = arrow.utcnow()
    
    workflow = {"name": "ObservationWorkflow",
                "comment": "Initialized workflow",
                "state": "draft",
                "last_transition": utc.datetime,
                "expires":  utc.replace(days=+7).datetime,
                "audit" : {'a': "init",
                           'r': "init",
                           'u': app.globals.get('user_id'),
                           's': None,
                           'd': "draft",
                           'v': _version,
                           't': utc.datetime,
                           'c': "Initialized workflow" }
                }
    
    watchers = [app.globals.get('user_id')]
    
    # Make a integer increment from seq collection
    seq = app.data.driver.db['seq']
    seq.update({'c': 'observations'}, {'$inc': {'i': int(1)}}, True) #,fields={'i': 1, '_id': 0},new=True).get('i')
    seq_r = seq.find_one({'c': 'observations'}, {'i': 1, '_id': 0})
    number = int(seq_r.get('i'))
    
    observation = app.data.driver.db['observations']
    observation.update({'_id': _id, '_etag': _etag}, 
                       { "$set": {"workflow": workflow,
                                  "id": number,
                                  "watchers": watchers, 
                                  "owner": app.globals.get('user_id'),
                                  "reporter": app.globals.get('user_id')
                                  } 
                        })
    
    pass

def observations_before_get(request, lookup):
    
    raise NotImplementedError
    pass

#app.on_pre_GET_observations += observations_before_get
#app.on_pre_POST_observations += observations_before_post
#app.on_pre_PATCH_observations += observations_before_patch
app.on_post_POST_observations += observations_after_post
app.on_post_PATCH_observations += observations_after_patch


"""
    Where can user id be added?
    Oplog comes with a auto feature for this
    @todo: Check the manual, verify with auth method choosen
"""
def before_insert_oplog(items):
    
    print(items)
    
app.on_insert_dev += before_insert_oplog





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
