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

# Authentication (blueprint)
from blueprints.authentication import Authenticate

# Melwin Search Blueprint
from blueprints.melwin_search import MelwinSearch

# Workflows as blueprints
from blueprints.observation_workflow import ObsWorkflow

# Cusotm url mappings (for flask)
from ext.url_maps import ObjectIDConverter

# Debug output use pprint
from pprint import pprint

# Custom extensions
from ext.tokenauth import TokenAuth

import sys




# Start Eve (and flask)
# Instantiate wit custom auth
#app = Eve(auth=TokenAuth)
app = Eve()

# Define global configs
app.globals = {"prefix": "/api/v1"}

app.globals.update({"auth": {}})
app.globals['auth'].update({"auth_collection": "users_auth",
                            "users_collection": "users",
                            })

pprint(app.globals)

# Start Bootstrap (should be a blueprint?)
Bootstrap(app)

#Custom url mapping
app.url_map.converters['objectid'] = ObjectIDConverter

# Register eve-docs blueprint 
app.register_blueprint(eve_docs, url_prefix="%s/docs" % app.globals['prefix'])

# Register custom blueprints
app.register_blueprint(Authenticate, url_prefix="%s/user" % app.globals['prefix'])
app.register_blueprint(MelwinSearch, url_prefix="%s/melwin/users/search" % app.globals['prefix'])

# Register workflow endpoints
app.register_blueprint(ObsWorkflow, url_prefix="%s/observations/workflow" % app.globals['prefix'])


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
    Start Eve & friends
    ===================
    
"""



"""

    Custom Flask routes 1:
    =====================
    
    Example using a flask route decorator with an external package
    
    Fetching yr.no data for all practical purposes just proxying via the route...
    
    Depends on libyr:
    >>>pip install git+https://github.com/wckd/python-yr.git
    
    Routes can also be packaged, say we have a 'avvik_custom_routes' package:
    import avvik_custom_routes
    And in the __init__.py the routes are defined, and makes this nice and clean!
    
    This is an example of a 'multiroute', ie the switch is the 'what' variable
    
    Also:
    =====
    
    Can also fetch data (forecast, metar & taf) as a supplement to the anomaly/avvik without user intervention

"""
@app.route("%s/weather/<what>" % app.globals['prefix'], methods=['GET'])
def wx(what):
    
    from yr.libyr import Yr #This should not be here
    weather = Yr(location_name='Norge/Vestfold/Tønsberg/Jarlsberg_flyplass')
    
    if what == 'now':
        return weather.now(as_json=True)
    
    elif what == 'forecast':
        return jsonify(**weather.dictionary['weatherdata']['forecast'])
    
    elif what == 'wind':
        wind_speed = dict()
        wind_speed['wind_forecast'] = [{'from': forecast['@from'], 'to': forecast['@to'],'@unit': 'knots', 'speed': round(float(forecast['windSpeed']['@mps'])*1.943844, 2)} for forecast in weather.forecast()]
        return jsonify(**wind_speed)
        
    else:
        return eve_error_msg('There is nothing defined for "' + what + '". Only /weather/now, /weather/wind and /weather/forecast are allowed.', 503)

"""
    Custom Flask routes 2:
    ======================
    
    Dummy stuff, simple as py....
    
    A catch all when not hitting correct path
    
    This should be blueprints from /apps/ directory per application

"""
@app.route("%s/info" % app.globals['prefix'], methods=['GET'])
def api_info():
    # Build a dictionary
    dict = {'api': 'F/NLF Elektroniske tjenester', 
            'version': '0.1.0', 
            'contact': 'Jan Erik Wang', 
            'email': 'Jan Erik Wang <janerik.wang@nlf.no>', 
            'api_url': request.base_url, 
            'doc_url': request.base_url + '/docs',
            'base_url': request.base_url,
            }
    
    # Jsonify the dictionary and return it
    return jsonify(**dict)


"""

    Event hooks:
    ============
    
    Using Eve events
    
    Applies to request and database makes it very extensible
    
    A more advanced use could be to emit a message through a websocket for every defined interaction.
    
    NB: To run a websocket server you need gunicorn or others with support for wsgi.websocket...

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
    #items['u'] = 45199
    
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
    
    Starting the wsgi development server with Eve
    
    Localhost and port 8080

"""
if __name__ == '__main__':
    port = 8080
    host = '127.0.0.1'

    app.run(host=host, port=port)
