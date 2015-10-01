
"""
    Custom tags increment
    =====================
    
    @note: Uses Eve by default, this only for incrementing freq, no need for _etag since we are inc and decrementing only!
    
    @todo:
    
"""

from flask import Blueprint, current_app as app, request, Response, abort, jsonify, send_file

from ext.app.decorators import *

Tags = Blueprint('Custom tags resource', __name__,)

@Tags.route("/freq/<objectid:tag_id>", methods=['POST'])
@require_token()
def increment(tag_id):
    
    return __increment(tag_id, 1)

@Tags.route("/freq/<objectid:tag_id>", methods=['DELETE'])
@require_token()
def decrement(tag_id):
    
    return __increment(tag_id, -1)



def __increment(tag_id, increment):
    """ Simple internal inc- and decrementer for freq
    """
    if increment in [1,-1]:
    
        try:
            tags = app.data.driver.db['tags']
    
            tags.update({'_id': tag_id}, { "$inc": {"freq": increment}} )
            
            return jsonify(**{'OK': True})
        
        except:
            
            return jsonify(**{'OK': False})
    
    # Should never end up here...        
    return jsonify(**{'OK': False})