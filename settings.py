"""
    Global Settings
    ===============

    Global Eve configuration settings
"""

import os, sys

# Make importing sliced up apps easy as pees
sys.path.insert(0, "domain")

# Import the apps - DOMAIN definition (app.DOMAIN)
import domain


__version_info__    = ('0', '4', '4-hotfix')
APP_VERSION         = '.'.join(__version_info__)
APP_AUTHOR          = 'Einar Huseby'
APP_LICENSE         = 'MIT'
APP_COPYRIGHT       = '(c) 2014-2016 F/NLF'
APP_ALL             = ['fnlf-backend']

# @TODO: use sys.argv to parse this as cmdline input
APP_INSTANCE = 'develop'  # develop || develop-local || production

if APP_INSTANCE == 'develop':
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    MONGO_USERNAME = ''
    MONGO_PASSWORD = ''
    MONGO_DBNAME = 'fnlf-dev'
    # Use default 30s?
    MONGO_CONNECT_TIMEOUT_MS = 200

    APP_HOST = '127.0.0.1'
    APP_PORT = 8081

elif APP_INSTANCE == 'develop-local':
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27018
    MONGO_USERNAME = ''
    MONGO_PASSWORD = ''
    MONGO_DBNAME = 'fnlf-dev'
    # Use default 30s?
    MONGO_CONNECT_TIMEOUT_MS = 200

    APP_HOST = '127.0.0.1'
    APP_PORT = 8081

elif APP_INSTANCE == 'production':
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    MONGO_USERNAME = ''
    MONGO_PASSWORD = ''
    MONGO_DBNAME = 'fnlf'
    MONGO_CONNECT_TIMEOUT_MS = 5000

    APP_HOST = '127.0.0.1'
    APP_PORT = 8080

# Will also make server watch inode and reload on changes
DEBUG = True

# Our api is located at */api/v1/
URL_PREFIX = 'api'
API_VERSION = 'v1'

# Pagination settings
PAGINATION_LIMIT = 1000
PAGINATION_DEFAULT = 50

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH) and deletes of individual items
# (defaults to read-only item access). PUT can be enabled to overwrite existing
ITEM_METHODS = ['GET', 'PATCH', 'DELETE', 'PUT']

# We enable standard client cache directives for all resources exposed by the
# API. We can always override these global settings later.
CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20

# Support only json response
XML = False
JSON = True

# Maximum value allowed for max_results query parameter
PAGINATION_LIMIT = 1000

ALLOW_UNKNOWN = False

# ISO
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# Will create on PUT wen not existing
#UPSERT_ON_PUT = True

# File storage
EXTENDED_MEDIA_INFO = ['content_type', 'name', 'length']
RETURN_MEDIA_AS_BASE64_STRING = True  # When true loads the file references as base64. Ok for (small) images, rubbish for files (video, documents) and large images Should make a seperate download/streaming resource

# CORS, see http://python-eve.org/config.html#global-configuration:
# X_DOMAINS = ['nlf-az.db02.cloudapp.net','kartverket.no']
# X_HEADERS = None
# X_EXPOSE_HEADERS = None
# X_MAX_AGE = 21600
X_DOMAINS = ['http://localhost:8081']
X_HEADERS = ['Content-Type', 'If-Match']  # Needed for the "Try it out" buttons
"""
    OP Log
    ======

    The OP Log logs all verbs on nouns

    NB: the collection should for any practical purposes be a capped collection so we don't fill it!!!

"""

OPLOG = False  # Set it to True to enable the Operations Log. Defaults to False.
OPLOG_NAME = 'oplog'  # This is the name of the database collection where the Operations Log is stored. Defaults to oplog.
OPLOG_METHODS = ['DELETE', 'POST', 'PATCH', 'PUT']  # List of HTTP methods which operations should be logged in the Operations Log. Defaults to ['DELETE', 'POST, 'PATCH', 'PUT'].
OPLOG_ENDPOINT = None #'oplog'  # Name of the Operations Log endpoint. If the endpoint is enabled it can be configured like any other API endpoint. Set it to None to disable the endpoint. Defaults to None.
OPLOG_AUDIT = True  # Set it to True to enable the audit feature. When audit is enabled client IP and document changes are also logged to the Operations Log. Defaults to True.
# OPLOG_CUSTOM_FIELDS = {'u': None}

SWAGGER_INFO = {
        'title': 'F/NLF API',
    'version': APP_VERSION,
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

# The DOMAIN dict explains which resources will be available and how they will
# be accessible to the API consumer.
DOMAIN = domain.DOMAIN
