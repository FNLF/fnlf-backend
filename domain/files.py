"""

    Files:
    ======
    
    Files are references in current document, and when loaded they output a base64 encoded string
    
    Use ?projection={"files": 0} to _not_ load files directly
    
"""

from _base import acl_schema

_schema = { 'name': {'type': 'string'},
            'description': {'type': 'string'},
            'tags': {'type': 'list'},
            'ref': {'type': 'string', 'required': True}, #say observations
            'ref_id': {'type': 'objectid','required': True}, #say ObjectId(545bda27a01ed25c57a10ad0) maybe a db ref?
            'file': {'type': 'media', 'required': True}, #Now, this is just a bunch of references is it?
            'acl': acl_schema,
            }

definition = {
        
        'item_title': 'files',
        'url': 'files',
        'description': 'Universal file storage and retrieval',
        'datasource': {
                       'source': 'files',
                       #'projection': {'file': 1}
               },
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH'],
        'versioning': True,        
        'schema': _schema,
        
}