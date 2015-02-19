
"""
    Custom files resource
    =====================
    
    @note: sizes: small, medium, large.
    
    @todo: Serve all kinds of files (pdf, doc etc)
    @todo: Serve video files - how??
    
"""

from flask import Blueprint, current_app as app, request, Response, abort, jsonify, send_file

from PIL import Image
import io
import mimetypes
from gridfs import GridFS
import base64

from ext.decorators import *

Files = Blueprint('Custom files resource', __name__,)

@Files.route("/<objectid:file_id>",defaults={'size': None}, methods=['GET'])
@Files.route("/<objectid:file_id>/<size>", methods=['GET'])
@require_token()
def serveImageFile(file_id, size):
    """ Resizes images to size and returns a base64 encoded string representing
    the image """ 
    
    sizes = {'small': (140,100),
             'medium': (400, 300),
             'large': (1200, 1000)}
    
    col = app.data.driver.db['files']
    
    image = col.find_one({'_id': file_id})
    
    grid_fs = GridFS(app.data.driver.db)
    
    if not grid_fs.exists(_id=image['file']):
        raise Exception("mongo gridfs file does not exist! {0}".format(id))
    
    im_stream = grid_fs.get_last_version(_id=image['file']) 
    
    im = Image.open(im_stream)
    
    if size:
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
