"""

    Observation comments
    ====================
    
    @note: Not working comments which are included inside the observation!
    
"""

_schema = {'user': {'type': 'integer',
                     'required': False}, #Because we hook it in!
           'comment': {'type': 'string',
                       'required': True},
           'observation': {'type': 'objectid',
                           'required': True}
           
           
           }

definition = {
        'item_title': 'observation_comments',
        'url' : 'observation/comments',
        'name': 'observation_comments',
        'datasource': {'source': 'observation_comments'},
        
        'versioning': False,
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET'],
        
        'schema': _schema
        
       }