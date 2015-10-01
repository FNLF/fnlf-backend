"""
    Eve compatible layer
    ====================
    
    Just a custom wrapper to resemble eve response for custom Flask endpoints
"""

from flask import jsonify, abort, Response
import json

def eve_abort(code, description):
    
    resp = Response(None, code)
    
    abort(code, description='You cant edit someone elses account', response=resp)


def eve_response(data):
    
    return Response(json.dumps(data, default=json_util.default),  mimetype='application/json')