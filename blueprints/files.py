
"""
    Custom files resource
    =====================
    
    @note: sizes: small, medium, large.
    
    @todo: Serve all kinds of files (pdf, doc etc)
    @todo: Serve video files - how??
    
"""

from flask import Blueprint, current_app as app, request, Response, abort, jsonify, send_file, abort, make_response

from PIL import Image
import io
import mimetypes
from gridfs import GridFS
from gridfs.errors import NoFile

import base64

from ext.app.decorators import *
from ext.auth.tokenauth import TokenAuth

Files = Blueprint('Custom files resource', __name__,)

@Files.route("/<objectid:file_id>", methods=['GET'])
#@require_token()
def process_request(file_id):
    """ This is the router actially for processing
    """
    
    if has_permission():
        col = app.data.driver.db['files']
        file = col.find_one({'_id': file_id})
        
        if not file:
            abort(404)
        
        try:
            grid_fs = GridFS(app.data.driver.db)
            if not grid_fs.exists(_id=file['file']):
                abort(404)
            
            stream = grid_fs.get_last_version(_id=file['file'])
            
            response = make_response(stream.read())
            response.mimetype = stream.content_type
            return response
        except NoFile:
            abort(404) 

@Files.route("/image/<objectid:file_id>",defaults={'size': None}, methods=['GET'])
@Files.route("/image/<objectid:file_id>/<string:size>", methods=['GET'])
@require_token()
def process_image_request(file_id, size):
    """ Resizes images to size and returns a base64 encoded string representing
    the image """ 
    
    sizes = {'small': (140,100),
             'medium': (400, 300),
             'large': (1200, 1000)
             }

    col = app.data.driver.db['files']
    image = col.find_one({'_id': file_id})
    
    grid_fs = GridFS(app.data.driver.db)
    
    if not grid_fs.exists(_id=image['file']):
        raise Exception("mongo gridfs file does not exist! {0}".format(id))
    
    im_stream = grid_fs.get_last_version(_id=image['file']) 
    
    im = Image.open(im_stream)
    
    if size != 'original':
        im.thumbnail(sizes[size], Image.ANTIALIAS)
    
    img_io = io.BytesIO()
    
    im.save(img_io, 'PNG', quality=100)
    img_io.seek(0)

    encoded_img = base64.b64encode(img_io.read())
    
    dict = {'mimetype': 'image/png',
            'encoding': 'base64', 
            'src': encoded_img
            }
    
    # Jsonify the dictionary and return it
    return jsonify(**dict)
    
    # Sends an image
    #return send_file(img_io, mimetype='image/png') 

@Files.route("/<objectid:file_id>/mimetype", methods=['GET'])
@require_token()
def get_file_mimetype(file_id):
    pass

def has_permission():
    
    try:
    
        b64token = request.args.get('token', default=None, type=str)
        token = base64.b64decode(b64token)[:-1]
        auth = TokenAuth()
                
        if not auth.check_auth(token=token.decode("utf-8"), 
                               method=request.method, 
                               resource=request.path[len(app.globals.get('prefix')):], 
                               allowed_roles=None):
            
            resp = Response(None, 401)
            abort(401, description='Please provide proper credentials', response=resp)

    except:
        resp = Response(None, 401)
        abort(401, description='Please provide proper credentials', response=resp)
    return True
    
    
