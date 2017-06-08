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
#from ext.app.decorators import async

CRITICAL_ERROR_CODES = [503]


def eve_abort(status=500, message='', sysinfo=None):
    """Abort processing and logging
    @Param: code http code
    @Param: message string representation"""
    try:
        status = int(status)
        if sysinfo == None:
            try:
                sysinfo = sys.exc_info()[0]
            except:
                pass

        resp = Response(None, status)

        if 100 <= status <= 299:
            #app.logger.info("%s: %s" % (message, sysinfo))
            pass
        elif 300 <= status <= 399:
            #app.logger.warn("%s: %s" % (message, sysinfo))
            pass
        elif 400 <= status <= 499:
            #app.logger.error("%s: %s" % (message, sysinfo))
            pass
        elif 500 <= status <= 599:
            # Check if mongo is down
            #app.logger.error("%s: %s" % (message, sysinfo))

            # 503 Service Unavailable
            if status in CRITICAL_ERROR_CODES:
                if not is_mongo_alive(status):
                    app.logger.critical("MongoDB is down [%s]" % sysinfo)
                    send_sms(status, "MongoDB is down (%s)" % app.config['APP_INSTANCE'])
                else:
                    app.logger.critical("%s [%s]" % (message, sysinfo))
                    message = message
                    send_sms(status, "%s (%s)" % (message, app.config['APP_INSTANCE']))

        else:
            #app.logger.debug("%s: %s" % (message, sysinfo))
            pass
    except:
        pass

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


def eve_response_get(data={}, status=200, error_message=False):
    return eve_response(data, status)

def eve_response_post(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


def eve_response_delete(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


def eve_response_put(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


def eve_response_patch(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


def is_mongo_alive(status=502):
    try:
        app.data.driver.db.command('ping')
        return True
    except:
        send_sms(status, "Mongodb is down (%s)" % app.config['APP_INSTANCE'])
        return False


def send_sms(status, message):
    try:
        sms = Sms()
        config = Scf()
        sms.send(mobile=config.get_warn_sms(), message="[%s] %s" % (status, message))
    except:
        pass
