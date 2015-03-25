"""
    Global Settings
    ===============
    
    Global Eve configuration settings
"""

import os, sys

# Make importing sliced up apps easy as pees
sys.path.insert(0,"domain")

# Import the apps - DOMAIN definition (app.DOMAIN)
import domain


# Running on local machine. Let's just use the local mongod instance.
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USERNAME = ''
MONGO_PASSWORD = ''
# Production
# MONGO_DBNAME = 'fnlf'
# Development
MONGO_DBNAME = 'fnlf-dev'

# Will also make server watch inode and reload on changes
DEBUG = True

# Our api is located at */api/v1/
URL_PREFIX = 'api'
API_VERSION = 'v1'


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

ALLOW_UNKNOWN = False

# ISO 
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# File storage
EXTENDED_MEDIA_INFO = ['content_type', 'name', 'length']
RETURN_MEDIA_AS_BASE64_STRING = True # When true loads the file references as base64. Ok for (small) images, rubbish for files (video, documents) and large images Should make a seperate download/streaming resource

# CORS, see http://python-eve.org/config.html#global-configuration:
#X_DOMAINS = ['nlf-az.db02.cloudapp.net','kartverket.no']
#X_HEADERS = None
#X_EXPOSE_HEADERS = None
#X_MAX_AGE = 21600

"""
    OP Log
    ======
    
    The OP Log logs all verbs on nouns
    
    NB: the collection should for any practical purposes be a capped collection so we don't fill it!!!
    
"""

OPLOG = True #Set it to True to enable the Operations Log. Defaults to False.
OPLOG_NAME = 'oplog' #This is the name of the database collection where the Operations Log is stored. Defaults to oplog.
OPLOG_METHODS = ['DELETE', 'POST', 'PATCH', 'PUT'] # List of HTTP methods which operations should be logged in the Operations Log. Defaults to ['DELETE', 'POST, 'PATCH', 'PUT'].
OPLOG_ENDPOINT = 'oplog' #Name of the Operations Log endpoint. If the endpoint is enabled it can be configured like any other API endpoint. Set it to None to disable the endpoint. Defaults to None.
OPLOG_AUDIT = True #Set it to True to enable the audit feature. When audit is enabled client IP and document changes are also logged to the Operations Log. Defaults to True.

# The DOMAIN dict explains which resources will be available and how they will
# be accessible to the API consumer.
DOMAIN = domain.DOMAIN
