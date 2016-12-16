"""
    Eve compatible layer
    ====================
    
    Just a custom wrapper to resemble eve response for custom Flask endpoints
"""

from flask import jsonify, abort, Response
import json


def eve_abort(code, message):
    
    resp = Response(None, code)

    abort(code, description=message, response=resp)


def eve_response(data):
    
    return Response(json.dumps(data, default=json_util.default),  mimetype='application/json')