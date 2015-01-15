"""

    Files:
    ======
    
    Test setup for file storage
    
    Files are references in current document, and when loaded they output a base64 encoded string
    
    Use ?projection={"files": 0} to _not_ load files directly. Seems like RETURN_MEDIA... do not work
    
    Have a common enpoint for streaming files??
    
    Could include image files or files in general up to a certain size? Server side generate thumbnails?? Internal rest call, so no external logic.
    
    Files are physically stored in gridFS, and versioning works perfect
    
    NB: This could be a resource where you only can access files directly not by the collection??

"""



_schema = {
            'name': {'type': 'string'},
            'description': {'type': 'string'},
            'belongs_resource': {'type': 'string'}, #say observations
            'belongs_id': {'type': 'string'}, #say ObjectId(545bda27a01ed25c57a10ad0) maybe a db ref?
            
            'file': {'type': 'media'}, #Now, this is just a bunch of references is it?
            }

definition = {
        
        'item_title': 'testfiles',
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'PUT'],
        'versioning': True,        
        'schema': _schema,
        'projection': {'file': 0}
}