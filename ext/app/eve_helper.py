"""
    Eve compatible layer
    ====================
    
    Just a custom wrapper to resemble eve response for custom Flask endpoints
"""

from flask import jsonify, abort, Response, current_app as app
import sys
import bson.json_util as json_util
import json


def eve_abort(status=500, message=''):
    """Abort processing
    @Param: code http code
    @Param: message string representation"""

    resp = Response(None, status)
    app.logger.info(message, sys.exc_info()[0])
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

    return Response(json.dumps(data, default=json_util.default), status=status, mimetype='application/json')


def eve_response_pppd(data={}, status=200, error_message=False):
    """Manually create a reponse for POST, PATCH, PUT, DELETE"""

    # Add status OK | ERR to data.
    if not error_message:
        data.update({'_status': 'OK'})
    else:
        data.update({'_status': 'ERR'})
        data.update({'_error': error_message})

    return eve_response(data, status)


def eve_response_post(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


def eve_response_delete(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


def eve_response_put(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)


def eve_response_patch(data={}, status=200, error_message=False):
    return eve_response_pppd(data, status, error_message)
