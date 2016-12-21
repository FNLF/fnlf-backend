"""
    FNLF-backend
    ============

    @todo: Need to implement tests! Eve got it's own tests which can be used, or eve-mocker?
    @todo: CI - via bamboo?



    @note: Pip stuff as a reminder
    
            Update all packages in one go!
            pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip install -U
            
            Find outdated packages
            pip list --outdated
    
    @note: Run as `nohup python run.py >> nlf.log 2>&1&` NB in virtualenv!
    
    @author:        Einar Huseby
    @copyright:     (c) 2014-2015 Fallskjermseksjonen Norges Luftsportsforbund
    @license:       MIT, see LICENSE for more details. Note that Eve is BSD licensed
"""

__version_info__ = ('0', '4', '4-hotfix')
__version__         = '.'.join(__version_info__)
__author__          = 'Einar Huseby'
__license__         = 'MIT'
__copyright__ = '(c) 2014-2016 F/NLF'
__all__             = ['fnlf-backend']

import os, sys
# from ext.app.custom_eve import CustomEve
from eve import Eve

# We need the json serializer from flask.jsonify (faster than "".json())
# flask.request for custom flask routes (no need for schemas, database or anything else)
from flask import jsonify, request, abort, Response

# Swagger docs
from eve_swagger import swagger

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
# from blueprints.melwin_updater import MelwinUpdater

# Custom url mappings (for flask)
from ext.app.url_maps import ObjectIDConverter, RegexConverter

# Custom auth extensions
from ext.auth.tokenauth import TokenAuth

# Debug output use pprint
from pprint import pprint

if not hasattr(sys, 'real_prefix'):
    print("Outside virtualenv, aborting....")
    sys.exit(-1)

# Make sure gunicorn passes settings.py
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.py')

# Start Eve (and flask)
# Instantiate with custom auth
#app = CustomEve(auth=TokenAuth, settings=SETTINGS_PATH)
#app = CustomEve(settings=SETTINGS_PATH)
app = Eve(auth=TokenAuth, settings=SETTINGS_PATH)




""" Define global settings
These settings are mirrored from Eve, but should not be!
@todo: use app.config instead
"""
app.globals = {"prefix": "/api/v1"}
app.globals.update({"auth": {}})
app.globals['auth'].update({"auth_collection": "users_auth",
                            "users_collection": "users"})

#Custom url mapping (needed by native flask routes)
app.url_map.converters['objectid']  = ObjectIDConverter
app.url_map.converters['regex']     = RegexConverter

# Register eve-docs blueprint 
#app.register_blueprint(eve_docs,        url_prefix="%s/docs" % app.globals.get('prefix'))
app.register_blueprint(swagger)
# You might want to simply update the eve settings module instead.
app.config['SWAGGER_INFO'] = {
        'title': 'F/NLF API',
    'version': __version__,
        'description': 'API to the F/NLF application framework',
    'termsOfService': 'Ole Brum',
        'contact': {
            'name': 'Jan Erik Wang',
            'email': 'janerik.wang@nlf.no',
            'url': 'https://www.nlf.no/fallskjerm'
        },
        'license': {
            'name': 'BSD',
            'url': 'https://github.com/FNLF/fnlf-backend/',
        }
}

# Register custom blueprints
app.register_blueprint(Authenticate,    url_prefix="%s/user" % app.globals.get('prefix'))
app.register_blueprint(MelwinSearch,    url_prefix="%s/melwin/users/search" % app.globals.get('prefix'))
app.register_blueprint(Weather,         url_prefix="%s/weather" % app.globals.get('prefix'))
app.register_blueprint(Info,            url_prefix="%s/info" % app.globals.get('prefix'))
app.register_blueprint(Files,           url_prefix="%s/download" % app.globals.get('prefix'))

# Register observation endpoints
app.register_blueprint(ObsWorkflow,     url_prefix="%s/observations/workflow" % app.globals.get('prefix'))
app.register_blueprint(ObsWatchers,     url_prefix="%s/observations/watchers" % app.globals.get('prefix'))
app.register_blueprint(Locations,       url_prefix="%s/locations" % app.globals.get('prefix'))
app.register_blueprint(Tags,            url_prefix="%s/tags" % app.globals.get('prefix'))
app.register_blueprint(ACL,             url_prefix="%s/users/acl" % app.globals.get('prefix'))
app.register_blueprint(ObsShare,        url_prefix="%s/observations/share" % app.globals.get('prefix'))
#app.register_blueprint(MelwinUpdater,   url_prefix="%s/muppet" % app.globals.get('prefix'))

""" A simple python logger setup
Eve do not yet support logging, but will for 0.5
Use app.logger.<level>(<message>) for manual logging
Levels: debug|info|warning|error|critical"""
if 1 == 1 or not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler('fnlf-backend.log', 'a', 1 * 1024 * 1024, 10)
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
                      "_error": {"message": message,
                                 "code": http_code}
                      })


"""
    Eve hooks
    ~~~~~~~~~
    
    This are located in ext.hooks package
"""
# Import hooks
import ext.hooks as hook

#app.on_insert_oplog += hook.oplog.before_insert

#app.on_pre_GET_observations += observations_before_get
#app.on_pre_POST_observations += observations_before_post
#app.on_pre_PATCH_observations += observations_before_patch
app.on_post_POST_observations += hook.observations.after_post
#app.on_pre_POST_observations += observations_before_post

app.on_pre_PATCH_observations += hook.observations.before_patch

app.on_post_PATCH_observations += hook.observations.after_patch

app.on_insert += hook.observations.before_post_comments
#app.on_insert_observation_comments += before_post_observation_comments

app.on_post_GET_observations += hook.observations.after_get

app.on_pre_GET_observations += hook.observations.before_get

app.on_pre_PATCH_observations += hook.observations.before_patch

"""
    Melwin updater via timer
"""
if 1 == 2:
    import ext.melwin.melwin_updater as updater

    if app.debug and not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        """Make sure to run only once"""
        updater.start(app)
        #melwin_updater.do_melwin_update(app)

"""

    START:
    ======
    
    Start the wsgi development server with Eve
    
    Localhost and port 8080
    
    @note: Run development server in background with log as 'nohup python run.py >> nlf.log 2>&1&' 
    @note: Run via gunicorn as 'gunicorn -w 5 -b localhost:8080 run:app'
    @note: Gunicorn should have 2n+1 workers where n is number of cpu cores
    @todo: Config file for gunicorn deployment and -C see http://gunicorn-docs.readthedocs.org/en/latest/settings.html

"""

if __name__ == '__main__':
    # Make sure we are on correct verions:
    if app.debug and not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        import pkg_resources

        print(" App:         %s" % __version__)
        print(" Eve:         %s" % pkg_resources.get_distribution("eve").version)
        print(" Cerberus:    %s" % pkg_resources.get_distribution("cerberus").version)
        print(" Flask:       %s" % pkg_resources.get_distribution("flask").version)
        print(" Pymongo:     %s" % pkg_resources.get_distribution("pymongo").version)
        print(" Pillow:      %s" % pkg_resources.get_distribution("Pillow").version)
        print(" Suds:        %s" % pkg_resources.get_distribution("suds-jurko").version)
        print(" Transtions:  %s" % pkg_resources.get_distribution("transitions").version)
        print(" Pytaf:       %s" % pkg_resources.get_distribution("pytaf").version)
        print(" Py Metar:    %s" % pkg_resources.get_distribution("python-metar").version)
        print(" Py YR:       %s" % pkg_resources.get_distribution("python-yr").version)
        print("--------------------------------------------------------------------------------")

    port = 8080
    host = '127.0.0.1'
    
    app.run(host=host, port=port)
