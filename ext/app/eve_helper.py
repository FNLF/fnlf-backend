"""
    Eve compatible layer
    ====================
    
    Just a custom wrapper to resemble eve response for custom Flask endpoints
"""

from flask import jsonify, abort, Response, current_app as app
import sys, json
import bson.json_util as json_util
from ..scf import Scf

from ext.notifications.sms import Sms  # Email
from ext.app.decorators import async

CRITICAL_ERROR_CODES = [503]

def eve_abort(status=500, message='', sysinfo=''):
    """Abort processing and logging
    @Param: code http code
    @Param: message string representation"""

    resp = Response(None, status)

    if 100 <= status <= 299:
        app.logger.info("%s: %s" % (message, sys.exc_info()[0]))
    elif 300 <= status <= 399:
        app.logger.warn("%s: %s" % (message, sys.exc_info()[0]))
    elif 400 <= status <= 499:
        app.logger.error("%s: %s" % (message, sys.exc_info()[0]))
    elif 500 <= status <= 599:
        # Check if mongo is down
        app.logger.error("%s: %s" % (message, sys.exc_info()[0]))

        # 503 Service Unavailable
        if status in CRITICAL_ERROR_CODES:
            if not is_mongo_alive(status):
                app.logger.critical("Mongo DB is DOWN %s" % sys.exc_info()[0])

    else:
        app.logger.debug("%s: %s" % (message, sys.exc_info()[0]))

    abort(status, description=message, response=resp)


def eve_response(data={}, status=200):
    """Manually send a response like Eve
    Uses Flask's Response object
    def __init__(self, response=None, status=None, headers=None,mimetype=None, content_type=None, direct_passthrough=False):
    """

    if isinstance(data, dict):
        pass
    elif isinstance(data, list):
        data = {'_items': data}
    elif isinstance(data, int):
        data = {'data': data}
    elif isinstance(data, str):
        data = {'data': data}

    try:
        resp = Response(json.dumps(data, default=json_util.default), status=status, mimetype='application/json')
    except:
        resp = jsonify(**data)
    return resp

def eve_response_pppd(data={}, status=200, error_message=False):
    """Manually create a reponse for POST, PATCH, PUT, DELETE"""

    # Add status OK | ERR to data.
    if not error_message:
        data.update({'_status': 'OK'})
    else:
        data.update({'_status': 'ERR'})
        data.update({'_error': error_message})

    return eve_response(data, status)


def eve_response_get(data={}, status=200):
    return eve_response(data, status)

def eve_response_post(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


def eve_response_delete(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


def eve_response_put(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


def eve_response_patch(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


# @async #If async, app is out of context!
def is_mongo_alive(status):
    try:
        app.data.driver.db.command('ping')
        return True
    except:
        sms = Sms()
        config = Scf()
        sms.send(mobile=config.get_warn_sms(), message="Http %i: Mongo er nede" % status)
        return False
